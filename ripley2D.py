from manim import *
from random import uniform
from scipy import spatial
import numpy as np

class GrowingCircleAndPlot(Scene):
    INITIAL_RADIUS = 0.4
    MAX_RADIUS = 2.25
    CIRCLE_COLOR = BLUE

    GROWTH_TIME = 20
    CREATION_TIME = 1
    WAIT_TIME = 0.5
    INITIAL_LABEL_SCALE = 0.5
    LABEL_OFFSET_FACTOR = 1.5

    SCENE_BUFF_LEFT = 3
    SCENE_BUFF_RIGHT = 1

    def construct(self):
        # Left side: Growing circle and radius
        circle, center_dot, radius_line, radius_label = self.create_growing_circle()
        circle_group = VGroup(circle, center_dot, radius_line, radius_label).to_edge(LEFT, buff=self.SCENE_BUFF_LEFT - 2)

        self.dots = self.get_dots()

        # Right side: Line plot
        plot = self.create_plot(circle).to_edge(RIGHT, buff=self.SCENE_BUFF_RIGHT).shift(DOWN * 0.3)
        self.axes = plot[0]

        # Create the full graph
        K_plot = self.axes.plot(self.K, color=RED, x_range=[0, 0])

        # Get reference line
        ref_line = self.axes.plot(self.ref_fn, color=GRAY)
        ref_line.set_stroke(opacity=0.8)

        # Create a vertical line on the plot
        self.vline, self.vline_label = self.create_vertical_line(self.axes, radius_line)

        # Create an equation and position it above the plot
        equation = MathTex(
            r"\hat{K}(r) = \frac{1}{\hat{\lambda}} \sum_{i} \sum_{j \neq i} I(d_{ij} < r)",
            color=WHITE
        )
        equation.next_to(plot, UP, buff=0.1).shift(RIGHT * 0.2)

        # Animate the scene
        self.wait(self.WAIT_TIME)
        self.play(Create(self.left_side_box), Create(circle), Create(center_dot), Create(plot), Create(DashedVMobject(ref_line)),
                  run_time=self.CREATION_TIME)
        self.play(Write(equation), run_time=self.CREATION_TIME)

        lines = VGroup(radius_line, self.vline)
        #labels = VGroup(radius_label, self.vline_label)
        labels = VGroup(radius_label)

        self.play(Create(lines), Create(labels), Create(K_plot), Create(self.dots), run_time=self.CREATION_TIME)

        K_plot.add_updater(self.update_graph)
        self.play(
            circle.animate.scale_to_fit_width(self.MAX_RADIUS * 2),
            UpdateFromFunc(radius_line, lambda line: self.update_radius_line(line, circle)),
            UpdateFromFunc(radius_label, lambda label: self.update_radius_label(label, radius_line, circle)),
            UpdateFromFunc(self.vline, lambda vline: self.update_vertical_line(vline,
                                                                               self.vline_label,
                                                                               self.axes,
                                                                               circle)),
            # UpdateFromFunc(self.vline_label, lambda vline_label: self.update_vline_label(radius_line,
            #                                                                              self.vline,
            #                                                                              vline_label)),
            rate_func=rate_functions.smootherstep,
            run_time=self.GROWTH_TIME
        )
        K_plot.remove_updater(self.update_graph)
        self.wait(self.WAIT_TIME)

    def create_growing_circle(self):
        """ Creates a growing circle with radius line and label. """
        # Create the rectangle
        self.left_side_box = Rectangle(
            width=5,  # Width of the left side
            height=7,  # Height of the scene
            stroke_color=WHITE,
            stroke_width=3,
            fill_color=BLACK,
            fill_opacity=0
        )
        self.left_side_box.to_edge(LEFT, buff=1)

        circle = Circle(radius=self.INITIAL_RADIUS, color=self.CIRCLE_COLOR)
        center_dot = Dot(point=circle.get_center(), color=GREEN)
        radius_line = self.create_radius_line(circle)
        radius_label = Tex("r").scale((0.35 * radius_line.get_length()/self.INITIAL_RADIUS) ** 0.5)
        self.position_label_above_line(radius_label, radius_line)

        return circle, center_dot, radius_line, radius_label

    def create_radius_line(self, circle):
        """ Creates a line representing the radius of a circle. """
        start_point = circle.get_center()
        end_point = circle.get_start()
        return Line(start_point, end_point, color=WHITE)

    def update_radius_line(self, line, circle):
        """ Updates the radius line to match the circle's current radius. """
        new_end_point = circle.get_start()
        line.put_start_and_end_on(line.get_start(), new_end_point)
        #print(line.get_length(), self.K(line.get_length()))

    def position_label_above_line(self, label, line):
        """ Positions the label above the center of the line. """
        midpoint = line.get_center()
        vertical_offset = UP * label.get_height() * self.LABEL_OFFSET_FACTOR
        label.move_to(midpoint + vertical_offset)

    def update_radius_label(self, label, line, circle):
        """ Updates the radius label's position and scale. """
        scale_factor = (0.35 * line.get_length() / self.INITIAL_RADIUS) ** 0.5
        label.set_height(Tex("r").get_height() * scale_factor)
        self.position_label_above_line(label, line)

    def create_plot(self, circle):
        """ Creates a line plot for the function K(r). """

        dot_pointlist = [dot.get_center() for dot in self.dots]
        #print(circle.get_center())
        self.dots_tree = spatial.cKDTree(dot_pointlist)
        #print("HERE", self.dots_tree)

        lam = self.left_side_box.get_width() * self.left_side_box.get_height() / (len(dot_pointlist) ** 2)

        # Create reference line
        self.ref_fn = lambda r: 1.5 * lam * np.pi * (r**2)

        # Define K(r) here. Example: K = lambda r: r**2
        self.K = lambda r: lam * len(self.dots_tree.query_ball_point(circle.get_center(), r))  # Replace with your actual function

        axes = Axes(
            x_range=[self.INITIAL_RADIUS, self.MAX_RADIUS, self.MAX_RADIUS/10.], y_range=[0, self.K(self.MAX_RADIUS), self.K(self.MAX_RADIUS)/10.],  # Adjust ranges as needed
            x_length=5, y_length=5,
            axis_config={"color": WHITE}
        )

        # Add X and Y axis labels
        x_label = MathTex("r").next_to(axes.x_axis, DOWN)
        y_label = MathTex("K(r)").next_to(axes.y_axis, LEFT)

        plot = VGroup(axes, x_label, y_label)
        return plot

    def create_vertical_line(self, axes, line):
        """ Creates an initial vertical line on the plot. """
        start_point = axes.c2p(self.INITIAL_RADIUS, 0)  # Starting at the leftmost part of the plot
        end_point = axes.c2p(self.INITIAL_RADIUS, self.K(self.INITIAL_RADIUS))  # Adjust the y-coordinate as needed
        vline = Line(start_point, end_point, color=WHITE)

        current_radius = 0.35 * line.get_length()
        scale_factor = (current_radius / self.INITIAL_RADIUS) ** 0.5

        vline_label = Tex("r").scale(self.INITIAL_LABEL_SCALE)
        vline_label.set_height(Tex("r").get_height() * scale_factor)
        vline_label.next_to(vline.get_center(), LEFT, buff=0.25)
        return vline, vline_label

    def update_vertical_line(self, vline, vline_label, axes, circle):
        """ Updates the position of the vertical line based on the circle's radius. """
        radius = circle.width / 2

        #print("Radius:", radius)
        #print("K:", self.K(4))
        start_point = axes.c2p(radius, 1e-6)
        end_point = axes.c2p(radius, self.K(radius))  # Adjust the y-coordinate as needed

        #if not (start_point==end_point).all():
        vline.put_start_and_end_on(start_point, end_point)
        vline_label.next_to(vline.get_center(), LEFT, buff=0.25)

    def update_vline_label(self, line, vline, vline_label):
        current_radius = 0.35 * line.get_length()
        scale_factor = (current_radius / self.INITIAL_RADIUS) ** 0.5
        vline_label.set_height(Tex("r").get_height() * scale_factor)
        vline_label.next_to(vline.get_center(), LEFT, buff=0.25)

    def update_graph(self, mob):
        # Function to reveal the graph based on the vertical line's position
        x_value = self.vline.get_start()[0]
        new_x_range = self.axes.p2c([x_value, 0, 0])[0]
        mob.become(self.axes.plot(self.K, color=RED, x_range=[self.INITIAL_RADIUS-0.01, new_x_range]))

    def get_dots(self):
        dots = VGroup()
        for _ in range(60):  # Adjust the number of dots as needed
            x = uniform(-5.9, -1.1)  # Random x-coordinate
            y = uniform(-3.4, 3.4)  # Random y-coordinate
            dot = Dot(point=[x, y, 0], radius=0.05, stroke_width=1, fill_opacity=0.75, color=RED)
            dots.add(dot)
        return dots
