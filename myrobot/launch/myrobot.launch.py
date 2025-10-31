import os
import xacro
from ament_index_python.packages import get_package_share_path, get_package_share_directory

from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration, Command

from launch.actions import ExecuteProcess, IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.conditions import UnlessCondition


from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    
    urdf_path                       = os.path.join(get_package_share_directory("myrobot"),
                                    "urdf", "myrobot.urdf.xacro",
                                    )   
    gazebo_ros_path                 = os.path.join(get_package_share_directory("gazebo_ros"),  
                                    "launch",
                                    )
    rviz_path                       = os.path.join(get_package_share_directory("myrobot"),  # Update with your package name
                                    "config", "myrobot_rviz2_cfg.rviz",
                                                )
    headless_mode = LaunchConfiguration('headless', default='true')
    robot_description_content = Command(['xacro ', urdf_path])
    robot_description = ParameterValue(robot_description_content, value_type=None)
   

    ## Launch RViz2
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_path],
        output='screen'
    )

    ## Joint State and Robot State Publisher Node 
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': True,'robot_description' : robot_description}]
    )

    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        parameters=[{'use_sim_time': True}],
        output='screen',
    )


    ## Load Gazebo server & Client and Spawn robot in Gazebo
    gazebo_server = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([gazebo_ros_path, '/gzserver.launch.py']),
                                    launch_arguments={'headless': headless_mode}.items()

    )
    gazebo_client = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([gazebo_ros_path, '/gzclient.launch.py']),
                                    launch_arguments={'headless': headless_mode}.items()
    )

    spawn_entity_node = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', '/robot_description', 
                   '-entity', 'myrobot'],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    return LaunchDescription([
        DeclareLaunchArgument('headless', 
            default_value='true', 
            description='Run Gazebo in headless mode'
        ),
        gazebo_server,
        gazebo_client,
        spawn_entity_node,
        rviz_node,
        robot_state_publisher_node,
        joint_state_publisher_node,

    ])

