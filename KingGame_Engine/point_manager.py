
class PointManager:
    # Points configuration for each round type
    POINTS_MAP: dict[str, int] = {
        'vazas': -20,
        'copas': -20,
        'homens': -30,
        'mulheres': -50,
        'king': -160,
        'last': -90,
        'nulos': -75,
        'positivo': 25,
    }

    NULOS_BASE_POINTS: int = 325

    @classmethod
    def get_points(cls, round_type: str, count: int) -> int:
        """Generic method to calculate points for any round type."""
        points_per_unit: int = cls.POINTS_MAP.get(round_type.lower(), 0)
        return points_per_unit * count

    # Keep individual methods for backwards compatibility
    @classmethod
    def get_points_vazas(cls, n_vazas: int) -> int:
        return cls.get_points('vazas', n_vazas)

    @classmethod
    def get_points_copas(cls, n_copas: int) -> int:
        return cls.get_points('copas', n_copas)

    @classmethod
    def get_points_homens(cls, n_homens: int) -> int:
        return cls.get_points('homens', n_homens)

    @classmethod
    def get_points_mulheres(cls, n_mulheres: int) -> int:
        return cls.get_points('mulheres', n_mulheres)

    @classmethod
    def get_points_king(cls, n_king: int) -> int:
        return cls.get_points('king', n_king)

    @classmethod
    def get_points_last(cls, n_last: int) -> int:
        return cls.get_points('last', n_last)

    @classmethod
    def get_points_nulos(cls, n_vazas: int, nulos: bool) -> int:
        """Calculate festa points based on nulos/positivo mode."""
        if nulos:
            return cls.NULOS_BASE_POINTS + cls.get_points('nulos', n_vazas)
        return cls.get_points('positivo', n_vazas)