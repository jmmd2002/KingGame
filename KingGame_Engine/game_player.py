from point_manager import PointManager

class GamePlayer():

    def __init__(self, id: int, name: str, is_ai: bool = False) -> None:
        self.id = id
        self.name = name
        self.is_ai = is_ai

        self.vazas = 0
        self.copas = 0
        self.homens = 0
        self.mulheres = 0
        self.king = 0
        self.last = 0

        self.festa1 = 0
        self.festa2 = 0
        self.festa3 = 0
        self.festa4 = 0

        # Nulos flags per festa (1=Nulos, 0=Positive)
        self.nulos_check = {f'Festa{i}': 1 for i in range(1,5)} # Default all to Nulos

    def get_total1(self) -> int:
        points_vazas = PointManager.get_points_vazas(self.vazas)
        points_copas = PointManager.get_points_copas(self.copas)
        points_homens = PointManager.get_points_homens(self.homens) 
        points_mulheres = PointManager.get_points_mulheres(self.mulheres) 
        points_king = PointManager.get_points_king(self.king) 
        points_last = PointManager.get_points_last(self.last)
        return points_vazas + points_copas + points_homens + points_mulheres + points_king + points_last
    
    def get_total(self) -> int:
        """Total including festa scores, optionally affected by Nulos/Positive."""
        festa_total = 0
        for i in range(1,5):
            festa_attr = getattr(self, f'festa{i}', 0)
            festa_total += PointManager.get_points_nulos(festa_attr, self.nulos_check.get(f'Festa{i}', 1))
        return self.get_total1() + festa_total