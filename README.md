# xboxdrv_monitor
## Adjusts xboxdrv configuration

- config file: /etc/xboxdrv/controller.json
- config_path: location of xboxdrv ini files
- num_controllers: number of controller to start. This can be set globally and per mapping.
- controller: controller configurations to load in order. 
  - Each configuration will be loaded and alwasy used for game specfic settings.
  - This should be the base configuration with xboxdrv, axismap, evdev-keymap and evdev-absmap sections
- mapping: array of custom configurations
  - proc_name: process name to monitor
  - proc_cmd: process arguments used to match process. 
    - This does not need to contain every argument. 
    - Only enough to identify the process.
   - config: array of config files to load for the process. 
     - This should contain ui-buttonmap and ui-axismap options to control game specific mappings
   - nowait_proc: boolean indicating if other processes can trigger configuration changes. 
     - If false or not specified monitoring will stop until the process exits preventing other processes from changing configs.

sample controller.json

```
{
"config_path":"/etc/xboxdrv",
"num_controllers":1,
"controller":[
        "rumblepad",
        "xpad"
],
"mapping":[
        {
        "config":
                [
                "mouse",
                "wasd",
                "minecraft"
                ],
        "proc_name":"java",
        "proc_cmd":
                [
                "-jar",
                "/opt/minecraft/Minecraft.jar"
                ]
        }
    ]
}
```
