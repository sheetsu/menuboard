from src.remote_control_manager import parse_data, browser_config, remote_control_task

if __name__=="__main__":
    hdmi1, hdmi2 = parse_data()
    driver_HDMI1, driver_HDMI2 = browser_config(hdmi1, hdmi2)
    remote_control_task(driver_HDMI1, driver_HDMI2)