from enum import Enum

# class syntax

LocalRegistrationType = Enum("LocalRegistrationType",
                             ["Point-to-Point ICP", "Point-to-Plane ICP", "Color ICP", "General ICP"], start=0)
