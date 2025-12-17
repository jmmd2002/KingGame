from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_migrate import Migrate

from database import db
from models import Player
from game_player import GamePlayer

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///players.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Make Python's getattr available in templates
app.jinja_env.globals.update(getattr=getattr)
migrate = Migrate(app, db)

db.init_app(app)

@app.template_filter('attr')
def attr(obj, name):
    return getattr(obj, name)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/leaderboard")
def leaderboard():
    # Get sorting preference from query parameter (default: points)
    sort_by = request.args.get('sort_by', 'points')
    
    # Calculate points and stats for each player
    players: list[Player] = Player.query.all()
    player_stats: list[dict] = []
    
    for player in players:
        # Handle None values from existing database records
        firsts = player.firsts or 0
        seconds = player.seconds or 0
        thirds = player.thirds or 0
        fourths = player.fourths or 0
        
        # Calculate points: 1st = 3pts, 2nd = 2pts, 3rd = 1pt, 4th = 0pts
        total_points = (firsts * 3) + (seconds * 2) + (thirds * 1) + (fourths * 0)
        total_games = firsts + seconds + thirds + fourths
        win_rate = (firsts / total_games * 100) if total_games > 0 else 0
        
        player_stats.append({
            'name': player.name,
            'firsts': firsts,
            'seconds': seconds,
            'thirds': thirds,
            'fourths': fourths,
            'total_games': total_games,
            'total_points': total_points,
            'win_rate': win_rate
        })
    
    # Sort based on selected criteria
    if sort_by == 'winrate':
        player_stats.sort(key=lambda x: (x['win_rate'], x['total_games']), reverse=True)
    else:  # default to points
        player_stats.sort(key=lambda x: (x['total_points'], x['total_games']), reverse=True)
    
    return render_template("leaderboard.html", player_stats=player_stats, sort_by=sort_by)

@app.route("/players")
def players():
    players = Player.query.all()
    return render_template("players.html", players=players)

@app.route("/add_player", methods=["POST"])
def add_player():
    name = request.form.get("name", "").strip()
    if not name:
        flash("Player name cannot be empty.")
        return redirect(url_for("players"))

    if Player.query.filter_by(name=name).first():
        flash("Player name must be unique.")
        return redirect(url_for("players"))

    player = Player(name=name)
    db.session.add(player)
    db.session.commit()
    flash("Player added successfully.")
    return redirect(url_for("players"))

@app.route("/delete_player/<int:player_id>")
def delete_player(player_id):
    player = Player.query.get_or_404(player_id)
    db.session.delete(player)
    db.session.commit()
    flash("Player deleted.")
    return redirect(url_for("players"))

@app.route("/edit_player/<int:player_id>", methods=["POST"])
def edit_player(player_id):
    player = Player.query.get_or_404(player_id)
    new_name = request.form.get("new_name", "").strip()

    if not new_name:
        flash("Player name cannot be empty.")
        return redirect(url_for("players"))

    if Player.query.filter_by(name=new_name).first():
        flash("That name is already taken.")
        return redirect(url_for("players"))

    player.name = new_name
    db.session.commit()
    flash("Player name updated.")
    return redirect(url_for("players"))

@app.route("/start_game")
def start_game():
    players = Player.query.all()
    return render_template("start_game.html", players=players)

@app.route("/game_table", methods=["POST"])
def game_table():
    selected_ids = request.form.getlist("players")

    if len(selected_ids) != 4:
        flash("You must select exactly 4 players.")
        return redirect(url_for("start_game"))

    selected_players = Player.query.filter(Player.id.in_(selected_ids)).all()
    game_players = [GamePlayer(id=p.id, name=p.name) for p in selected_players]

    totals_1fase = {gp.id: gp.get_total1() for gp in game_players}
    totals_final = {gp.id: gp.get_total() for gp in game_players}

    session["game_data"] = {gp.id: gp.__dict__ for gp in game_players}

    return render_template(
        "game_table.html",
        players=game_players,
        totals_1fase=totals_1fase,
        totals_final=totals_final
    )


@app.route("/submit_game_table", methods=["POST"])
def submit_game_table():
    game_data = session.get("game_data")
    if not game_data:
        flash("Game session expired.")
        return redirect(url_for("index"))

    game_players = []
    for pid, pdata in game_data.items():
        gp = GamePlayer(id=pdata["id"], name=pdata["name"])
        # Set main rounds
        for attr in ['vazas','copas','homens','mulheres','king','last',
                     'festa1','festa2','festa3','festa4']:
            setattr(gp, attr, pdata.get(attr, 0))
        # Restore nulos_check
        gp.nulos_check = pdata.get('nulos_check', {f'Festa{i}':1 for i in range(1,5)})
        game_players.append(gp)

    rounds = ['Vazas','Copas','Homens','Mulheres','King','Last']
    festas = ['Festa1','Festa2','Festa3','Festa4']

    # --- Update all scores from form ---
    for gp in game_players:
        # main rounds
        for round_name in rounds:
            key = f"score_{round_name}_{gp.id}"
            value = request.form.get(key, 0)
            try:
                setattr(gp, round_name.lower(), int(value))
            except (ValueError, TypeError):
                setattr(gp, round_name.lower(), 0)

        # festa rounds
        for i, festa in enumerate(festas, start=1):
            key = f"score_{festa}_{gp.id}"
            value = request.form.get(key, 0)
            try:
                setattr(gp, f'festa{i}', int(value))
            except (ValueError, TypeError):
                setattr(gp, f'festa{i}', 0)

    # --- Update nulos per row (same for all players) ---
    for i, festa in enumerate(festas, start=1):
        nulos_value = request.form.get(f"nulos_{festa}", "1")
        for gp in game_players:
            gp.nulos_check[festa] = int(nulos_value)

    # Compute totals
    totals_1fase = {gp.id: gp.get_total1() for gp in game_players}
    totals_final = {gp.id: gp.get_total() for gp in game_players}

    # Update session
    session["game_data"] = {gp.id: gp.__dict__ for gp in game_players}

    return render_template(
        "game_table.html",
        players=game_players,
        totals_1fase=totals_1fase,
        totals_final=totals_final
    )

@app.route("/finish_game", methods=["POST"])
def finish_game():
    game_data = session.get("game_data")
    if not game_data:
        flash("Game session expired.")
        return redirect(url_for("index"))

    # Rebuild players from session + update scores from form
    game_players = []
    rounds = ['Vazas','Copas','Homens','Mulheres','King','Last']
    festas = ['Festa1','Festa2','Festa3','Festa4']

    for pid, pdata in game_data.items():
        gp = GamePlayer(id=pdata["id"], name=pdata["name"])
        # restore attributes
        for attr in rounds + festas:
            value = request.form.get(f"score_{attr}_{gp.id}", 0)
            setattr(gp, attr.lower(), int(value))
        # restore nulos_check
        gp.nulos_check = {festa: int(request.form.get(f"nulos_{festa}", 1)) for festa in festas}
        game_players.append(gp)

    # Compute totals
    totals_1fase = {gp.id: gp.get_total1() for gp in game_players}
    totals_final = {gp.id: gp.get_total() for gp in game_players}

    # Compute ranks (highest rank for ties)
    sorted_players = sorted(game_players, key=lambda p: p.get_total(), reverse=True)
    ranks_fields = ['firsts', 'seconds', 'thirds', 'fourths']
    position = 0
    player_ranks = {}

    while position < len(sorted_players):
        current_total = sorted_players[position].get_total()
        tied_players = [p for p in sorted_players[position:] if p.get_total() == current_total]
        rank_index = position
        for p in tied_players:
            if rank_index < len(ranks_fields):
                player_ranks[p.id] = rank_index + 1
                # Update player stats in database
                db_player = Player.query.get(p.id)
                if db_player:
                    current_value = getattr(db_player, ranks_fields[rank_index], 0)
                    setattr(db_player, ranks_fields[rank_index], current_value + 1)
        position += len(tied_players)

    db.session.commit()

    # Clear game session since game is finished
    session.pop("game_data", None)

    flash("Game finished! Rankings saved to database.")

    # Render same table with updated totals and ranks
    return render_template(
        "game_table.html",
        players=game_players,
        totals_1fase=totals_1fase,
        totals_final=totals_final,
        player_ranks=player_ranks
    )



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)