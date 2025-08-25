import math
import matplotlib.pyplot as plt

class RecursiveConvolution:
    def __init__(self):
        """
        Initialize the class with default parameters and state variables.
        """
        self.g0 = None
        self.g1 = None
        self.g2 = None
        self.alpha = None
        self.omega = None
        self.prev_y1 = 0  # Store the previous output value y[n-1]
        self.prev_y2 = 0  # Store the previous output value y[n-2]
        self.prev_x = 0   # Store the previous input value x[n-1]
        self.dt = None    # The time step size

    def update_parameters(self, b, m, k, dt):
        """
        Update the system parameters and compute g[0] and g[1].

        Parameters:
        b (float): Damping coefficient.
        m (float): Mass.
        k (float): Spring constant.
        dt (float): Time step size.
        """
        # Compute alpha and omega
        self.alpha = b / (2 * m)
        self.omega = math.sqrt(max(0, k / m - self.alpha ** 2))  # Natural frequency

        self.g0 = b / m

        # Precompute g[1] for the given parameters
        self.g1 = (
            (b / m) * math.exp(-self.alpha * dt) * math.cos(self.omega * dt) +
            ((k - (b ** 2) / (2 * m)) / (m * self.omega)) * math.exp(-self.alpha * dt) * math.sin(self.omega * dt)
        )

        self.dt = dt  # Store the time step size

    def calculate_output(self, x):
        """
        Compute the output y[n] for the given input x[n].

        Parameters:
        x (float): Current input value x[n].

        Returns:
        float: Output value y[n].
        """
        if self.g1 is None or self.dt is None:
            raise ValueError("System parameters not initialized. Call 'update_parameters' first.")

        # Compute the coefficients for the recursive calculation
        exp_neg_alpha_dt = math.exp(-self.alpha * self.dt)
        cos_term = math.cos(self.omega * self.dt)
        exp_neg_2alpha_dt = math.exp(-2 * self.alpha * self.dt)

        # Recursive calculation
        y = (
            2 * exp_neg_alpha_dt * cos_term * self.prev_y1 -
            exp_neg_2alpha_dt * self.prev_y2 +
            self.dt * self.g0 * x +
            self.dt * (self.g1 - 2 * exp_neg_alpha_dt * self.g0 * cos_term) * self.prev_x
        )

        # Update state variables
        self.prev_y2 = self.prev_y1
        self.prev_y1 = y
        self.prev_x = x

        return y

if __name__ == "__main__":
    # Initialize the convolution system
    conv = RecursiveConvolution()

    # Update parameters (e.g., b=1, m=1, k=10, dt=0.01)
    b, m, k, dt = 1, 1, 10, 0.001
    conv.update_parameters(b=b, m=m, k=k, dt=dt)

    # Generate unit step response
    num_points = 10000
    time_points = [n * dt for n in range(num_points)]
    unit_step_input = [1 for n in range(num_points)]  # Unit step input

    # Calculate the output for the unit step input
    unit_step_output = []
    for x in unit_step_input:
        y = conv.calculate_output(x)
        unit_step_output.append(y)

    # Plot the output
    plt.figure(figsize=(10, 6))
    plt.plot(time_points, unit_step_output, label="Unit Step Response")
    plt.title("Unit Step Response of the System")
    plt.xlabel("Time (s)")
    plt.ylabel("Output y[n]")
    plt.grid(True)
    plt.legend()
    plt.show()
