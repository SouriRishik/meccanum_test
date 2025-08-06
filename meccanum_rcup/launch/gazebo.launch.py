from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from ament_index_python.packages import get_package_share_directory
import os
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
import xacro

def generate_launch_description():
    share_dir = get_package_share_directory('meccanum_rcup')

    # Gazebo world path
    world = os.path.join(
        get_package_share_directory('turtlebot3_gazebo'),
        'worlds',
        'turtlebot3_world.world'  # Replace with your world file if needed
    )

    # Xacro file for robot description
    xacro_file = os.path.join(share_dir, 'urdf', 'meccanum_rcup.xacro')
    robot_description_config = xacro.process_file(xacro_file)
    robot_urdf = robot_description_config.toxml()

    # Robot spawn position
    x_pose = LaunchConfiguration('x_pose', default='-2.0')
    y_pose = LaunchConfiguration('y_pose', default='0.0')

    # Declare Launch Arguments
    declare_x_pose_cmd = DeclareLaunchArgument(
        'x_pose', default_value='-2.0', description='X position for spawning the robot'
    )

    declare_y_pose_cmd = DeclareLaunchArgument(
        'y_pose', default_value='0.0', description='Y position for spawning the robot'
    )

    # Robot state publisher node
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[{'robot_description': robot_urdf}],
    )

    # Gazebo server and client
    gzserver_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('gazebo_ros'), 'launch', 'gzserver.launch.py')
        ),
        launch_arguments={'world': world}.items()
    )

    gzclient_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('gazebo_ros'), 'launch', 'gzclient.launch.py')
        )
    )

    # Spawn the robot in Gazebo
    urdf_spawn_node = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'meccanum_rcup',
            '-topic', 'robot_description',
            '-x', LaunchConfiguration('x_pose'),
            '-y', LaunchConfiguration('y_pose')
        ],
        output='screen',
    )

    return LaunchDescription([
        declare_x_pose_cmd,
        declare_y_pose_cmd,
        robot_state_publisher_node,
        gzserver_cmd,
        gzclient_cmd,
        urdf_spawn_node
    ])
