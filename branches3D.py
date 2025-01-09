from manim import ThreeDScene, Cube, DEGREES, Write, Unwrite, UP, DOWN, VGroup, LEFT, RIGHT, OUT, IN
import numpy as np
from kernels_subset import KERNELS

def test():
    pass

class Rotation3DExample(ThreeDScene):
    def construct(self):

        self.begin_ambient_camera_rotation(rate=0.3)
        self.set_camera_orientation(phi=75*DEGREES, theta=30*DEGREES)

        for k in KERNELS:
            cubes_1 = VGroup(*[Cube(side_length=1, fill_opacity=np.array(k[0]).flatten()[c]) for c in range(0, 9)])
            cubes_2 = VGroup(*[Cube(side_length=1, fill_opacity=np.array(k[1]).flatten()[c]) for c in range(0, 9)])
            cubes_3 = VGroup(*[Cube(side_length=1, fill_opacity=np.array(k[2]).flatten()[c]) for c in range(0, 9)])

            cubes_1.arrange_in_grid(rows=3, cols=3, buff=0.01)
            cubes_2.arrange_in_grid(rows=3, cols=3, buff=0.01)
            cubes_3.arrange_in_grid(rows=3, cols=3, buff=0.01)

            cubes_1.next_to(cubes_2, OUT, buff=0.01)
            cubes_3.next_to(cubes_2, IN, buff=0.01)


            self.play(
                Write(cubes_1),
                Write(cubes_2),
                Write(cubes_3),
                run_time=0.3
            )

            self.wait(1.5)

            self.play(
                Unwrite(cubes_1),
                Unwrite(cubes_2),
                Unwrite(cubes_3),
                run_time=0.3
            )

        self.wait(1)

if __name__ == "__main__":
    test()