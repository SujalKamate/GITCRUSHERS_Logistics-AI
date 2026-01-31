"""
Symbolic mathematical models for logistics simulation using SymPy.

These models provide:
- Truck trajectory equations
- Fuel consumption formulas
- Traffic delay calculations
- Cost optimization functions
"""
import sympy as sp
from sympy import Symbol, Function, Eq, solve, diff, integrate, sqrt, exp, log
from typing import Dict, Any, Tuple
import structlog

logger = structlog.get_logger(__name__)


class SymbolicModels:
    """
    Collection of symbolic mathematical models for logistics.

    Uses SymPy for symbolic computation allowing:
    - Exact solutions where possible
    - Parameter sensitivity analysis
    - Optimization problem formulation
    """

    def __init__(self):
        """Initialize symbolic variables and base equations."""
        # Time variable
        self.t = Symbol('t', positive=True, real=True)

        # Distance and position
        self.d = Symbol('d', positive=True, real=True)  # distance
        self.x = Symbol('x', real=True)  # x position
        self.y = Symbol('y', real=True)  # y position

        # Velocity
        self.v = Symbol('v', positive=True, real=True)  # velocity
        self.v_max = Symbol('v_max', positive=True, real=True)  # max velocity
        self.v_traffic = Symbol('v_traffic', positive=True, real=True)  # traffic-adjusted velocity

        # Traffic
        self.traffic_factor = Symbol('tau', positive=True, real=True)  # traffic delay factor

        # Fuel
        self.fuel_rate = Symbol('f_rate', positive=True, real=True)  # fuel consumption rate
        self.fuel_total = Symbol('F', positive=True, real=True)  # total fuel available

        # Cost
        self.cost_fuel = Symbol('c_fuel', positive=True, real=True)  # cost per liter
        self.cost_time = Symbol('c_time', positive=True, real=True)  # cost per hour
        self.cost_driver = Symbol('c_driver', positive=True, real=True)  # driver cost per hour

        # Weight/Load
        self.weight = Symbol('W', positive=True, real=True)  # load weight

        logger.info("Symbolic models initialized")

    # =========================================================================
    # Trajectory Models
    # =========================================================================

    def position_equation(self, v: float = None) -> sp.Expr:
        """
        Position as a function of time at constant velocity.

        x(t) = v * t

        Args:
            v: Optional specific velocity value

        Returns:
            Symbolic expression for position
        """
        velocity = v if v is not None else self.v
        return velocity * self.t

    def time_to_destination(self, distance: float = None, velocity: float = None) -> sp.Expr:
        """
        Time required to travel a given distance.

        t = d / v

        Args:
            distance: Distance in km
            velocity: Velocity in km/h

        Returns:
            Time expression or value
        """
        d = distance if distance is not None else self.d
        v = velocity if velocity is not None else self.v
        return d / v

    def effective_velocity(self, base_velocity: float = None, traffic_factor: float = None) -> sp.Expr:
        """
        Effective velocity considering traffic.

        v_eff = v_base / traffic_factor

        Traffic factor: 1.0 = free flow, 2.0 = double time, etc.

        Args:
            base_velocity: Base velocity without traffic
            traffic_factor: Traffic delay multiplier

        Returns:
            Effective velocity expression
        """
        v = base_velocity if base_velocity is not None else self.v_max
        tau = traffic_factor if traffic_factor is not None else self.traffic_factor
        return v / tau

    def trajectory_with_traffic(
        self,
        segments: list[Tuple[float, float, float]]
    ) -> Tuple[sp.Expr, float]:
        """
        Calculate trajectory through multiple segments with different traffic.

        Args:
            segments: List of (distance_km, base_speed_kmh, traffic_factor) tuples

        Returns:
            Tuple of (total_time_expression, total_distance)
        """
        total_time = sp.Integer(0)
        total_distance = 0.0

        for dist, speed, traffic in segments:
            effective_speed = speed / traffic
            segment_time = dist / effective_speed
            total_time += segment_time
            total_distance += dist

        return total_time, total_distance

    # =========================================================================
    # Fuel Consumption Models
    # =========================================================================

    def fuel_consumption_basic(self, distance: float = None, rate: float = None) -> sp.Expr:
        """
        Basic fuel consumption model.

        F = rate * distance

        Args:
            distance: Distance in km
            rate: Consumption rate in L/km

        Returns:
            Fuel consumption expression
        """
        d = distance if distance is not None else self.d
        r = rate if rate is not None else self.fuel_rate
        return r * d

    def fuel_consumption_with_load(
        self,
        distance: float = None,
        base_rate: float = 0.3,
        weight: float = None,
        weight_factor: float = 0.00002
    ) -> sp.Expr:
        """
        Fuel consumption model accounting for load weight.

        F = (base_rate + weight_factor * weight) * distance

        Args:
            distance: Distance in km
            base_rate: Base consumption rate L/km
            weight: Load weight in kg
            weight_factor: Additional consumption per kg

        Returns:
            Fuel consumption expression
        """
        d = distance if distance is not None else self.d
        w = weight if weight is not None else self.weight

        effective_rate = base_rate + weight_factor * w
        return effective_rate * d

    def fuel_consumption_with_speed(
        self,
        distance: float = None,
        speed: float = None,
        optimal_speed: float = 60.0
    ) -> sp.Expr:
        """
        Fuel consumption model accounting for speed (less efficient at high/low speeds).

        F = base_rate * distance * (1 + 0.01 * (v - v_optimal)^2 / v_optimal)

        Args:
            distance: Distance in km
            speed: Average speed in km/h
            optimal_speed: Most fuel-efficient speed

        Returns:
            Fuel consumption expression
        """
        d = distance if distance is not None else self.d
        v = speed if speed is not None else self.v

        efficiency_factor = 1 + 0.01 * ((v - optimal_speed) ** 2) / optimal_speed
        return self.fuel_rate * d * efficiency_factor

    # =========================================================================
    # Cost Models
    # =========================================================================

    def total_cost(
        self,
        distance: float = None,
        time_hours: float = None,
        fuel_liters: float = None,
        fuel_price: float = 1.5,
        driver_rate: float = 25.0,
        vehicle_rate: float = 10.0
    ) -> sp.Expr:
        """
        Total cost of a trip.

        Cost = fuel_price * fuel + (driver_rate + vehicle_rate) * time

        Args:
            distance: Distance in km
            time_hours: Trip duration in hours
            fuel_liters: Fuel consumption in liters
            fuel_price: Price per liter
            driver_rate: Driver cost per hour
            vehicle_rate: Vehicle operating cost per hour

        Returns:
            Total cost expression
        """
        t = time_hours if time_hours is not None else self.t
        f = fuel_liters if fuel_liters is not None else self.fuel_total

        fuel_cost = fuel_price * f
        time_cost = (driver_rate + vehicle_rate) * t

        return fuel_cost + time_cost

    def delay_cost(
        self,
        delay_hours: float = None,
        penalty_rate: float = 50.0,
        is_critical: bool = False
    ) -> sp.Expr:
        """
        Cost of delay for late delivery.

        Args:
            delay_hours: Hours past deadline
            penalty_rate: Penalty per hour
            is_critical: If True, double the penalty

        Returns:
            Delay cost expression
        """
        delay = delay_hours if delay_hours is not None else Symbol('delay', positive=True)
        multiplier = 2 if is_critical else 1
        return multiplier * penalty_rate * delay

    # =========================================================================
    # Optimization Models
    # =========================================================================

    def optimal_speed_for_deadline(
        self,
        distance: float,
        time_available: float,
        max_speed: float = 100.0
    ) -> float:
        """
        Calculate optimal speed to meet deadline.

        Args:
            distance: Distance to travel in km
            time_available: Time available in hours
            max_speed: Maximum allowed speed

        Returns:
            Required speed in km/h
        """
        required_speed = distance / time_available

        if required_speed > max_speed:
            logger.warning(
                "Cannot meet deadline at max speed",
                required=required_speed,
                max_speed=max_speed
            )
            return max_speed

        return required_speed

    def route_comparison(
        self,
        routes: list[Dict[str, Any]]
    ) -> Dict[str, Dict[str, float]]:
        """
        Compare multiple routes on various metrics.

        Args:
            routes: List of route dictionaries with:
                - name: Route name
                - distance_km: Total distance
                - traffic_factor: Average traffic factor
                - base_speed_kmh: Base speed

        Returns:
            Comparison matrix with metrics for each route
        """
        comparison = {}

        for route in routes:
            name = route['name']
            dist = route['distance_km']
            traffic = route.get('traffic_factor', 1.0)
            speed = route.get('base_speed_kmh', 60)

            # Calculate metrics
            effective_speed = speed / traffic
            time_hours = dist / effective_speed
            fuel = self.fuel_consumption_basic(dist, 0.3)
            cost = float(self.total_cost(
                distance=dist,
                time_hours=time_hours,
                fuel_liters=float(fuel)
            ))

            comparison[name] = {
                'distance_km': dist,
                'time_hours': float(time_hours),
                'fuel_liters': float(fuel),
                'total_cost': cost,
                'effective_speed_kmh': float(effective_speed),
            }

        return comparison

    def minimize_cost_with_constraint(
        self,
        max_time: float,
        distance: float,
        min_speed: float = 30,
        max_speed: float = 100
    ) -> Dict[str, float]:
        """
        Find optimal speed to minimize cost while meeting time constraint.

        Args:
            max_time: Maximum time allowed in hours
            distance: Distance in km
            min_speed: Minimum allowed speed
            max_speed: Maximum allowed speed

        Returns:
            Dictionary with optimal speed and expected metrics
        """
        # Speed needed to meet deadline
        required_speed = distance / max_time

        if required_speed > max_speed:
            return {
                'feasible': False,
                'optimal_speed': max_speed,
                'time_hours': distance / max_speed,
                'meets_deadline': False,
            }

        if required_speed < min_speed:
            required_speed = min_speed

        # For fuel efficiency, optimal speed is around 60 km/h
        # But we need to meet the deadline
        optimal = max(required_speed, 60.0) if max_time > distance / 60 else required_speed

        time_hours = distance / optimal
        fuel = float(self.fuel_consumption_basic(distance, 0.3))
        cost = float(self.total_cost(
            distance=distance,
            time_hours=time_hours,
            fuel_liters=fuel
        ))

        return {
            'feasible': True,
            'optimal_speed': optimal,
            'time_hours': time_hours,
            'fuel_liters': fuel,
            'total_cost': cost,
            'meets_deadline': time_hours <= max_time,
        }

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def evaluate(self, expr: sp.Expr, **kwargs) -> float:
        """
        Evaluate a symbolic expression with given values.

        Args:
            expr: SymPy expression
            **kwargs: Variable name to value mappings

        Returns:
            Numerical result
        """
        substitutions = {}
        for name, value in kwargs.items():
            symbol = getattr(self, name, None)
            if symbol is not None:
                substitutions[symbol] = value

        result = expr.subs(substitutions)
        return float(result)

    def sensitivity_analysis(
        self,
        expr: sp.Expr,
        variable: str,
        base_value: float,
        range_percent: float = 20
    ) -> Dict[str, float]:
        """
        Perform sensitivity analysis on an expression.

        Args:
            expr: Expression to analyze
            variable: Variable name to vary
            base_value: Base value of variable
            range_percent: Percentage range to test

        Returns:
            Dictionary with sensitivity results
        """
        symbol = getattr(self, variable, None)
        if symbol is None:
            raise ValueError(f"Unknown variable: {variable}")

        # Calculate derivative
        derivative = diff(expr, symbol)

        # Evaluate at base value and variations
        low_value = base_value * (1 - range_percent / 100)
        high_value = base_value * (1 + range_percent / 100)

        base_result = float(expr.subs(symbol, base_value))
        low_result = float(expr.subs(symbol, low_value))
        high_result = float(expr.subs(symbol, high_value))

        return {
            'base_value': base_value,
            'base_result': base_result,
            'low_value': low_value,
            'low_result': low_result,
            'high_value': high_value,
            'high_result': high_result,
            'sensitivity': (high_result - low_result) / (high_value - low_value),
        }
