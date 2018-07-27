from __future__ import absolute_import, division, print_function

import inspect
import xml.etree.ElementTree as ET

from compas.files import URDF
from compas.geometry import Frame, Rotation, Vector

# URDF is defined in meters
# so we scale it all to millimeters
SCALE_FACTOR = 1000

__all__ = ['Robot', 'Joint', 'Link', 'Inertial', 'Visual', 'Collision', 'Geometry', 'MeshDescriptor', 'Origin', 'Mass', 'Inertia', 'ParentJoint', 'ChildJoint', 'Calibration', 'Dynamics', 'Limit', 'Axis', 'Mimic', 'SafetyController']


class Origin(object):
    """Reference frame represented by an instance of :class:`Frame`."""

    @classmethod
    def from_urdf(cls, attributes, elements, text):
        xyz = [float(i) * SCALE_FACTOR for i in attributes.get('xyz', '0 0 0').split(' ')]
        rpy = list(map(float, attributes.get('rpy', '0 0 0').split(' ')))
        xform = Rotation.from_axis_angle_vector(rpy, xyz)
        return Frame.from_transformation(xform)


class Mass(object):
    """Represents a value of mass usually related to a link."""

    def __init__(self, value):
        self.value = float(value)

    def __str__(self):
        return str(self.value)


class Inertia(object):
    """Rotational inertia matrix (3x3) represented in the inertia frame.

    Since the rotational inertia matrix is symmetric, only 6 above-diagonal
    elements of this matrix are specified here, using the attributes
    ``ixx``, ``ixy``, ``ixz``, ``iyy``, ``iyz``, ``izz``.
    """

    def __init__(self, ixx=0., ixy=0., ixz=0., iyy=0., iyz=0., izz=0.):
        # TODO: Check if we need unit conversion here (m to mm?)
        self.ixx = float(ixx)
        self.ixy = float(ixy)
        self.ixz = float(ixz)
        self.iyy = float(iyy)
        self.iyz = float(iyz)
        self.izz = float(izz)


class Inertial(object):
    """Inertial properties of a link.

    Attributes:
        origin: This is the pose of the inertial reference frame,
            relative to the link reference frame.
        mass: Mass of the link.
        inertia: 3x3 rotational inertia matrix, represented in the inertia frame.
    """

    def __init__(self, origin=None, mass=None, inertia=None):
        self.origin = origin
        self.mass = mass
        self.inertia = inertia

class MeshDescriptor(object):
    """Description of a mesh."""

    def __init__(self, filename, scale=1.0):
        self.filename = filename
        self.scale = scale

class Geometry(object):
    """Shape of a link."""

    def __init__(self, box=None, cylinder=None, sphere=None, mesh=None):
        self.shape = box or cylinder or sphere or mesh
        if not self.shape:
            raise ValueError('Geometry must define at least one of: box, cylinder, sphere, mesh')

class Visual(object):
    """Visual description of a link.

    Attributes:
        geometry: Shape of the visual element.
        origin: Reference frame of the visual element with respect
            to the reference frame of the link.
        name: Name of the visual element.
        material: Material of the visual element.
    """

    def __init__(self, geometry, origin=None, name=None, material=None):
        self.geometry = geometry
        self.origin = origin
        self.name = name
        self.material = material


class Collision(object):
    """Collidable description of a link.

    Attributes:
        geometry: Shape of the collidable element.
        origin: Reference frame of the collidable element with respect
            to the reference frame of the link.
        name: Name of the collidable element.
    """

    def __init__(self, geometry, origin=None, name=None):
        self.geometry = geometry
        self.origin = origin
        self.name = name


class Link(object):
    """Link represented as a rigid body with an inertia, visual, and collision features.

    Attributes:
        name: Name of the link itself.
        type: Link type. Undocumented in URDF, but used by PR2.
        visual: Visual properties of the link.
        collision: Collision properties of the link. This can be different
            from the visual properties of a link.
        inertial: Inertial properties of the link.
        attr: Non-standard attributes.
    """

    def __init__(self, name, type=None, visual=[], collision=[], inertial=None, **kwargs):
        self.name = name
        self.type = type
        self.visual = visual
        self.collision = collision
        self.inertial = inertial
        self.attr = kwargs


class ParentJoint(object):
    """Describes a parent relation between joints."""

    def __init__(self, link):
        self.link = link

    def __str__(self):
        return str(self.link)


class ChildJoint(object):
    """Describes a child relation between joints."""

    def __init__(self, link):
        self.link = link

    def __str__(self):
        return str(self.link)


class Calibration(object):
    """Reference positions of the joint, used to calibrate the absolute position."""

    def __init__(self, rising=0.0, falling=0.0, reference_position=0.0):
        self.rising = float(rising)
        self.falling = float(falling)
        self.reference_position = float(reference_position)


class Dynamics(object):
    """Physical properties of the joint used for simulation of dynamics."""

    def __init__(self, damping=0.0, friction=0.0):
        self.damping = float(damping)
        self.friction = float(friction)


class Limit(object):
    """Joint limit properties.

    Attributes:
        effort: Maximum joint effort.
        velocity: Maximum joint velocity.
        lower: Lower joint limit (radians for revolute joints, millimeter for prismatic joints).
        upper: Upper joint limit (radians for revolute joints, millimeter for prismatic joints).
    """

    def __init__(self, effort, velocity, lower=0.0, upper=0.0):
        self.effort = float(effort)
        self.velocity = float(velocity)
        # TODO: Scale upper/lower limits once this is connected to a joint, if the joint is prismatic
        self.lower = float(lower)
        self.upper = float(upper)


class Mimic(object):
    """Description of joint mimic."""

    def __init__(self, joint, multiplier=1.0, offset=0):
        self.joint = joint
        self.multiplier = multiplier
        self.offset = offset


class SafetyController(object):
    """Safety controller properties."""

    def __init__(self, k_velocity, k_position=0.0, soft_lower_limit=0.0, soft_upper_limit=0.0):
        self.k_velocity = float(k_velocity)
        self.k_position = float(k_position)
        self.soft_lower_limit = float(soft_lower_limit)
        self.soft_upper_limit = float(soft_upper_limit)


class Axis(object):
    """Representation of an axis or vector."""

    def __init__(self, xyz='0 0 0'):
        # We are not using Vector here because we
        # cannot attach _urdf_source to it due to __slots__
        xyz = [float(i) * SCALE_FACTOR for i in xyz.split(' ')]
        self.x = xyz[0]
        self.y = xyz[1]
        self.z = xyz[2]


class Joint(object):
    """Representation of the kinematics and dynamics of a
    joint and its safety limits.

    Attributes:
        name: Unique name for the joint.
        type: Joint type.
        origin: Transformation from the parent link to the child link frame.
        parent: Name of the parent link.
        child: Name of the child link.
        axis: Joint axis specified in the joint frame. Represents the axis of rotation
            for revolute joints, the axis of translation for prismatic joints, and
            the surface normal for planar joints. The axis is specified in the joint
            frame of reference.
        calibration: Reference positions of the joint, used to calibrate the absolute
            position of the joint.
        dynamics: Physical properties of the joint. These values are used to specify
            modeling properties of the joint, particularly useful for simulation.
        limit: Joint limit properties.
        safety_controller: Safety controller properties.
        mimic: Used to specify that the defined joint mimics another existing joint.
        attr: Non-standard attributes.
    """
    SUPPORTED_TYPES = ('revolute', 'continuous', 'prismatic',
                       'fixed', 'floating', 'planar')

    def __init__(self, name, type, parent, child, origin=None, axis=None, calibration=None, dynamics=None, limit=None, safety_controller=None, mimic=None, **kwargs):
        if type not in (Joint.SUPPORTED_TYPES):
            raise ValueError('Unsupported joint type: %s' % type)

        self.name = name
        self.type = type
        self.parent = parent
        self.child = child
        self.origin = origin
        self.axis = axis
        self.calibration = calibration
        self.dynamics = dynamics
        self.limit = limit
        self.safety_controller = safety_controller
        self.mimic = mimic
        self.attr = kwargs


class Robot(object):
    """Robot is the root of the model.

    Robot instances are the root node in a tree structure representing an entire robot.

    In line with URDF limitations, only tree structures can be represented by this
    model, ruling out all parallel robots.
    """

    def __init__(self, name, joints=[], links=[], material=None, transmission=None, **kwargs):
        self.name = name
        self.joints = joints
        self.links = links
        self.material = material
        self.transmission = transmission
        self.attr = kwargs

    @classmethod
    def from_urdf_file(cls, file):
        """Construct a Robot model from a URDF file model description.

        Args:
            file: file name or file object.

        Returns:
            A robot model instance.
        """
        return URDF.parse(file)

    @classmethod
    def from_urdf_string(cls, text):
        """Construct a Robot model from a URDF description as string.

        Args:
            text: string containing the XML URDF model.

        Returns:
            A robot model instance.
        """
        return URDF.from_string(text)


URDF.add_parser('robot', Robot)
URDF.add_parser('joint', Joint)
URDF.add_parser('link', Link)
URDF.add_parser('inertial', Inertial)
URDF.add_parser('visual', Visual)
URDF.add_parser('collision', Collision)
URDF.add_parser('geometry', Geometry)
URDF.add_parser('mesh', MeshDescriptor)
URDF.add_parser('origin', Origin)
URDF.add_parser('mass', Mass)
URDF.add_parser('inertia', Inertia)
URDF.add_parser('parent', ParentJoint)
URDF.add_parser('child', ChildJoint)
URDF.add_parser('calibration', Calibration)
URDF.add_parser('dynamics', Dynamics)
URDF.add_parser('limit', Limit)
URDF.add_parser('axis', Axis)
URDF.add_parser('mimic', Mimic)
URDF.add_parser('safety_controller', SafetyController)
