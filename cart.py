import pygame
import sys
import math

# =============================================================================
# CONFIGURATION PARAMETERS
# =============================================================================

# Screen configuration
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BG_COLOR = (255, 255, 255)

# -----------------------------------------------------------------------------
# Cart Configurations
# -----------------------------------------------------------------------------
# For each cart we define two offsets:
#   - spring_contact_offset: where the spring attaches (shifted upward)
#   - connector_contact_offset: where the connector box attaches (shifted downward)
outer_cart_config = {
    "pos": pygame.Vector2(400, 300),           # Center position of the outer cart
    "width": 400,
    "height": 200,
    "color": (0, 0, 255),
    "spring_contact_offset": pygame.Vector2(-200, 50),   # For spring connection (moved up)
    "connector_contact_offset": pygame.Vector2(200, 20)    # For connector box connection (moved down)
}

inner_cart_config = {
    "pos": pygame.Vector2(400, 350),           # Center position of the inner cart (nested within outer cart)
    "width": 100,
    "height": 50,
    "color": (0, 0, 180),
    "spring_contact_offset": pygame.Vector2(-50, 0),  # For spring connection (moved up)
    "connector_contact_offset": pygame.Vector2(50, 0)   # For connector box connection (moved down)
}

# -----------------------------------------------------------------------------
# Spring Configuration (connecting the carts’ spring connection points)
# -----------------------------------------------------------------------------
spring_config = {
    "num_coils": 10,
    "amplitude": 10
}

# -----------------------------------------------------------------------------
# Connector Box Configuration
# -----------------------------------------------------------------------------
# The connector box is a fixed-size black rectangle with its own two connection
# points. Its connections (relative to its center) are defined as follows:
#   - outer: where the variable (dampener) leg attaches to the outer cart.
#   - inner: where the fixed, horizontal leg attaches to the inner cart.
#
# The fixed leg length (used for the inner leg) is specified by 'fixed_leg_length'.
# A new parameter 'contact_y_proportion' (0.0 = top, 1.0 = bottom) determines
# the vertical placement of the contact points along the box's edge.
# Additionally, an indicator rectangle is drawn on the inner side of the box.
connector_box_config = {
    "pos": pygame.Vector2(400, 330),               # Initial position (will be updated relative to the inner cart)
    "width": 80,
    "height": 40,
    "color": (0, 0, 0),
    # Offsets for the connector box’s own connection points (only the x value is used; y is overridden below):
    "contact_offset_outer": pygame.Vector2(40, 20),  # Outer connection point (right side)
    "contact_offset_inner": pygame.Vector2(-40, 0), # Inner connection point (left side)
    "fixed_leg_length": 15,                          # Fixed horizontal distance for the inner leg
    "contact_y_proportion": 0.5,                     # 1.0 means bottom edge; use 0.5 for center, etc.
    "indicator_color": (255, 255, 0),                # Color of the indicator rectangle
    "indicator_size": (10, 30)                       # Size of the indicator rectangle (width, height)
}

# -----------------------------------------------------------------------------
# Animation Parameters (for demonstration)
# -----------------------------------------------------------------------------
outer_cart_motion = {
    "amplitude": 50,   # Horizontal oscillation amplitude (pixels)
    "phase": 0
}

inner_cart_motion = {
    "amplitude": 30,   # Horizontal oscillation amplitude (pixels)
    "phase": math.pi/4
}

# =============================================================================
# PYGAME INITIALIZATION
# =============================================================================

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Connection Points, Spring, and Connector Box")
clock = pygame.time.Clock()

# =============================================================================
# CLASS DEFINITIONS
# =============================================================================

class ConnectionPoint:
    """
    Represents a connection point with its own measurable quantities.
    It stores its current absolute position (pos) and the displacement (dx, dy)
    since the last update.
    """
    def __init__(self, parent, offset):
        """
        parent: the object to which this connection point is attached.
                (The parent is expected to have a 'pos' attribute.)
        offset: a pygame.Vector2 representing the offset from the parent's position.
        """
        self.parent = parent
        self.offset = pygame.Vector2(offset)
        self.pos = self.parent.pos + self.offset  # initial absolute position
        self.displacement = pygame.Vector2(0, 0)
    
    def update(self):
        """
        Update the connection point's absolute position based on the parent's current position.
        Also, compute its displacement (change in position).
        """
        new_pos = self.parent.pos + self.offset
        self.displacement = new_pos - self.pos
        self.pos = new_pos

    def draw(self, surface, color=(255, 0, 0), radius=5):
        pygame.draw.circle(surface, color, (int(self.pos.x), int(self.pos.y)), radius)

class Cart:
    """
    A rectangular cart with two independent connection points:
      - spring_connection: for the spring attachment.
      - connector_connection: for the connector box attachment.
    """
    def __init__(self, pos, width, height, color, spring_offset, connector_offset):
        self.pos = pygame.Vector2(pos)
        self.width = width
        self.height = height
        self.color = color
        # Create connection points as independent entities.
        self.spring_connection = ConnectionPoint(self, spring_offset)
        self.connector_connection = ConnectionPoint(self, connector_offset)
    
    def update(self, displacement=pygame.Vector2(0,0)):
        self.pos += displacement
        # Update both connection points.
        self.spring_connection.update()
        self.connector_connection.update()
    
    def draw(self, surface):
        rect = pygame.Rect(
            self.pos.x - self.width/2,
            self.pos.y - self.height/2,
            self.width,
            self.height
        )
        pygame.draw.rect(surface, self.color, rect)
    
    def debug_draw(self, surface):
        # Draw the connection points (for debugging)
        self.spring_connection.draw(surface, color=(255,0,0))
        self.connector_connection.draw(surface, color=(255,0,255))

class Spring:
    """
    A sinusoidal spring that connects two connection points.
    """
    def __init__(self, pointA, pointB, num_coils, amplitude):
        self.pointA = pointA  # expects a ConnectionPoint
        self.pointB = pointB
        self.num_coils = num_coils
        self.amplitude = amplitude

    def draw(self, surface):
        start = self.pointA.pos
        end = self.pointB.pos
        direction = end - start
        length = direction.length()
        if length == 0:
            return
        direction.normalize_ip()
        perp = pygame.Vector2(-direction.y, direction.x)
        num_points = self.num_coils * 20  # More points for smoothness
        points = []
        for i in range(num_points+1):
            t = i / num_points
            # Taper the oscillation amplitude toward the endpoints.
            offset = math.sin(t * self.num_coils * math.pi * 2) * self.amplitude * (1 - abs(t - 0.5)*2)
            point = start + direction * (t * length) + perp * offset
            points.append((int(point.x), int(point.y)))
        pygame.draw.lines(surface, (0, 255, 0), False, points, 2)

class ConnectorBox:
    """
    A fixed-size black rectangle with its own two connection points.
    It draws two legs connecting its connection points to the carts’ connector connection points.
      - The inner leg is fixed: it is drawn purely horizontally with a fixed length.
      - The outer leg is drawn as a variable segment, but its endpoints are forced to share the same y-coordinate.
    Additionally, red circles are drawn at the connector box's connection points, and a small indicator
    rectangle is drawn on the side corresponding to the fixed (inner) leg.
    """
    def __init__(self, pos, width, height, color, outer_offset, inner_offset, fixed_leg_length):
        self.pos = pygame.Vector2(pos)
        self.width = width
        self.height = height
        self.color = color
        self.fixed_leg_length = fixed_leg_length
        # Create the connector box's own connection points.
        self.outer_connection = ConnectionPoint(self, outer_offset)
        self.inner_connection = ConnectionPoint(self, inner_offset)
        # Use the new parameter for adjusting the vertical placement of both contact points.
        self.contact_y_proportion = connector_box_config.get("contact_y_proportion", 1.0)
        # Indicator parameters:
        self.indicator_color = connector_box_config.get("indicator_color", (255,255,0))
        self.indicator_size = connector_box_config.get("indicator_size", (10,10))
    
    def update(self):
        # Update the box's own connection points.
        self.outer_connection.update()
        self.inner_connection.update()
        # Force the y-coordinate of both connection points to be the same,
        # based on the contact_y_proportion. Compute the y coordinate along the box.
        new_y = self.pos.y - self.height/2 + self.contact_y_proportion * self.height
        self.outer_connection.pos = pygame.Vector2(self.outer_connection.pos.x, new_y)
        self.inner_connection.pos = pygame.Vector2(self.inner_connection.pos.x, new_y)
    
    def draw(self, surface, outer_cart_cp, inner_cart_cp):
        """
        Draw the connector box and its legs.
          outer_cart_cp: the outer cart's connector connection (a ConnectionPoint)
          inner_cart_cp: the inner cart's connector connection (a ConnectionPoint)
        """
        # Draw the connector box (filled rectangle)
        rect = pygame.Rect(
            self.pos.x - self.width/2,
            self.pos.y - self.height/2,
            self.width,
            self.height
        )
        pygame.draw.rect(surface, self.color, rect)
        
        # Draw the indicator rectangle on the inner side (fixed leg side).
        # For example, draw a small rectangle flush with the left edge.
        indicator_width, indicator_height = self.indicator_size
        indicator_rect = pygame.Rect(
            self.pos.x - self.width/2,  # left edge of the box
            self.pos.y - self.height/2 + (self.height - indicator_height)/2,  # vertically centered
            indicator_width,
            indicator_height
        )
        pygame.draw.rect(surface, self.indicator_color, indicator_rect)
        
        # Update our own connection points.
        self.update()
        
        # --- Draw the inner leg (fixed horizontal leg) ---
        # For the fixed (inner) leg, force the y-coordinate to be identical.
        inner_target = pygame.Vector2(inner_cart_cp.pos.x, self.inner_connection.pos.y)
        pygame.draw.line(surface, (0,0,0),
                         (int(self.inner_connection.pos.x), int(self.inner_connection.pos.y)),
                         (int(inner_target.x), int(inner_target.y)), 2)
        
        # --- Draw the outer leg (variable leg) ---
        # For the outer leg, force the y-coordinate to match the box's outer connection point.
        outer_target = pygame.Vector2(outer_cart_cp.pos.x, self.outer_connection.pos.y)
        pygame.draw.line(surface, (0,0,0),
                         (int(self.outer_connection.pos.x), int(self.outer_connection.pos.y)),
                         (int(outer_target.x), int(outer_target.y)), 2)
        
        # Draw red circles (contact points) on the connector box.
        self.outer_connection.draw(surface, color=(255,0,0))
        self.inner_connection.draw(surface, color=(255,0,0))

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

# =============================================================================
# OBJECT INITIALIZATION
# =============================================================================

# Create Cart objects.
outer_cart = Cart(
    pos=outer_cart_config["pos"],
    width=outer_cart_config["width"],
    height=outer_cart_config["height"],
    color=outer_cart_config["color"],
    spring_offset=outer_cart_config["spring_contact_offset"],
    connector_offset=outer_cart_config["connector_contact_offset"]
)

inner_cart = Cart(
    pos=inner_cart_config["pos"],
    width=inner_cart_config["width"],
    height=inner_cart_config["height"],
    color=inner_cart_config["color"],
    spring_offset=inner_cart_config["spring_contact_offset"],
    connector_offset=inner_cart_config["connector_contact_offset"]
)

# Create the Spring connecting the carts' spring connection points.
spring = Spring(
    pointA=inner_cart.spring_connection,
    pointB=outer_cart.spring_connection,
    num_coils=spring_config["num_coils"],
    amplitude=spring_config["amplitude"]
)

# Create the ConnectorBox.
connector_box = ConnectorBox(
    pos=connector_box_config["pos"],
    width=connector_box_config["width"],
    height=connector_box_config["height"],
    color=connector_box_config["color"],
    outer_offset=connector_box_config["contact_offset_outer"],
    inner_offset=connector_box_config["contact_offset_inner"],
    fixed_leg_length=connector_box_config["fixed_leg_length"]
)

# Create convolution object

conv = RecursiveConvolution()

conv.update_parameters(b=185, m=500, k=1500, dt=1/60)

# =============================================================================
# MAIN LOOP
# =============================================================================

outer_cart_velocity = pygame.Vector2(0, 0) # 2D velocity, only x is used
outer_cart_displacement = pygame.Vector2(0, 0) # position of the cart relative to its initial position

cart_speed = 100; # pixels/second

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_LEFT]:
        outer_cart_velocity.x = -cart_speed
    elif keys[pygame.K_RIGHT]:
        outer_cart_velocity.x = cart_speed
    else:
        outer_cart_velocity.x = 0
    

    # Clear screen
    screen.fill(BG_COLOR)

    # -------------------------------------------------------------------------
    # UPDATE SECTION (Animation / Dynamics)
    # -------------------------------------------------------------------------
    t = pygame.time.get_ticks() / 1000.0  # time in seconds

    # Update cart positions with sinusoidal horizontal motion (for demonstration)
    outer_cart.pos += outer_cart_velocity * (1/60) # multiply by constant frametime, just assumed
    outer_cart_displacement = outer_cart.pos - pygame.Vector2(outer_cart_config["pos"]) # positional vector with reference at the starting position
    #inner_cart.pos.x = inner_cart_config["pos"].x + inner_cart_motion["amplitude"] * math.sin(t + inner_cart_motion["phase"])
    
    #Compute convolution for position of inner cart
    
    inner_cart.pos.x = inner_cart_config["pos"].x + conv.calculate_output(outer_cart_displacement.x)
    
    # Update the carts’ connection points.
    outer_cart.update()
    inner_cart.update()
    
    # --- Update the connector box position based on the inner cart ---
    # We want the inner leg (from the inner cart to the connector box) to be purely horizontal
    # with a fixed length. Thus, we set the connector box's position so that its inner connection point
    # is exactly fixed_leg_length to the right of the inner cart's connector connection.
    fixed_leg_length = connector_box_config["fixed_leg_length"]
    # inner cart's connector connection position:
    inner_cp = inner_cart.connector_connection.pos  
    # And the connector box's inner connection is defined as (box.pos + inner_offset).
    # To force a fixed horizontal separation, update the box position:
    connector_box.pos = inner_cp + pygame.Vector2(fixed_leg_length, 0) - connector_box_config["contact_offset_inner"]
    
    # -------------------------------------------------------------------------
    # DRAWING SECTION
    # -------------------------------------------------------------------------
    # Draw carts
    outer_cart.draw(screen)
    inner_cart.draw(screen)
    
    # (Optional) Debug-draw the carts' connection points:
    # outer_cart.debug_draw(screen)
    inner_cart.debug_draw(screen)
    
    # Draw the spring connecting the carts’ spring connection points.
    spring.draw(screen)
    # Optionally draw the spring connection points:
    outer_cart.spring_connection.draw(screen, color=(255,0,0))
    inner_cart.spring_connection.draw(screen, color=(255,0,0))
    
    # Draw the connector box and its legs.
    # The connector box attaches to the carts’ connector connection points.
    connector_box.draw(screen,
                         outer_cart_cp=outer_cart.connector_connection,
                         inner_cart_cp=inner_cart.connector_connection)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
