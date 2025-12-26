# This code required learning of new materials
# Everything that wasn't covered in CSCI 203 that I have used here -- including but not limited to: new methods, 
# 3animation function, pandas dataframes and series, tuple unpacking, graphing plots in grid, and using APIs -- comes from watching reading matplotlib documentaion, fastf1 documentation, 
# W3 Schools, GeeksForGeeks, Stack Overflow, and watching a few YouTube totorials


from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import fastf1
import fastf1.plotting as fp


fastf1.plotting.setup_mpl(color_scheme='fastf1')
fp.set_default_colormap('official')

   
def initialize_session():
    year = int(input('Year: '))
    series_of_gp = fastf1.events.get_event_schedule(year)['Location']
    
    gp = input('GP (choose from above): ')
    session_type = input('Session Type (ex: Q - Qualifying, R - Race): ')
    session = fastf1.get_session(year, gp, session_type)
    session.load()
    
    list_of_driver_num = session.drivers

    for index in range(len(list_of_driver_num)):
        num_id = list_of_driver_num[index]
        driver_dataframe = session.get_driver(num_id)
        driver_short = driver_dataframe['Abbreviation']
        print(driver_short)    

    
    driver = input('Driver (ex: HAM): ')
    

    return year, gp, driver, session  


def get_data(driver, stored_session):
    # extracting all ther required data

    laps_of_driver = stored_session.laps.pick_drivers(driver)
    fastest_lap = laps_of_driver.pick_fastest()
    telemetry_table = fastest_lap.get_telemetry()

    # TIME SERIES
    lap_time_in_s = (fastest_lap['LapTime'].total_seconds())
    lap_time_in_ms = lap_time_in_s * 1000
    time_series = telemetry_table['Time']
    for i in range(len(time_series)):
        time_series.iloc[i] = round(time_series.iloc[i].total_seconds(), 3)


    # CAR-RELATED SERIES
    x_pos_series = telemetry_table['X']
    y_pos_series = telemetry_table['Y']
    velocity_series = telemetry_table['Speed']
    braking_series = telemetry_table['Brake']
    gear_series = telemetry_table['nGear']
    throttle_series = telemetry_table['Throttle']

    # CIRCUIT CORNERS
    cc_info = stored_session.get_circuit_info()
    x_corners = cc_info.corners['X']
    y_corners = cc_info.corners['Y']

    return fastest_lap, lap_time_in_s, lap_time_in_ms, time_series, x_pos_series, y_pos_series, velocity_series, gear_series, throttle_series, x_corners, y_corners


def track_plot_limit(stored_fast_lap):
    fast_pos_data = stored_fast_lap.get_pos_data()

    fast_x = fast_pos_data['X']
    fast_y = fast_pos_data['Y']

    fast_x_min = min(fast_x) - 1000
    fast_x_max = max(fast_x) + 1000 
    fast_y_min = min(fast_y) - 1000
    fast_y_max = max(fast_y) + 1000

    return fast_x_min, fast_x_max, fast_y_min, fast_y_max

    

def animation_plot(stored_driver, stored_gp, stored_year, stored_fastest_lap, stored_lap_time_in_s, stored_lap_time_in_ms, stored_time_series,
                   stored_x_pos_series, stored_y_pos_series, stored_velocity_series, stored_gear_series,
                   stored_throttle_series, stored_x_corners, stored_y_corners, pos_x_min, pos_x_max, pos_y_min, pos_y_max):
    # setting up the main plot
    fig, main_axis = plt.subplots()
    plt.title(f"{stored_driver} | {stored_gp} Grand Prix | {stored_year}")
    fig.set_figheight(10)
    fig.set_figwidth(10)
    main_axis.set_xticks([])
    main_axis.set_yticks([])

    # POSITION PLOT
    position_axis = plt.subplot2grid(shape=(20,5), loc=(0,0), colspan=(5), rowspan=(8))
    position_axis.set_xlim([pos_x_min, pos_x_max])  # width of track 
    position_axis.set_ylim([pos_y_min, pos_y_max]) # height of track 
    position_axis.set_xticks([])
    position_axis.set_yticks([])


    # VELOCITY PLOT 
    velocity_axis = plt.subplot2grid(shape=(2,2), loc=(1,0), colspan=(1))
    velocity_axis.set_xlabel('time (s)')
    velocity_axis.set_ylabel('speed (km / h)')
    velocity_axis.set_xlim([0, stored_lap_time_in_s])  # width of track 
    velocity_axis.set_ylim([0, max(stored_velocity_series) + 20]) # height of track 

    # CURRENT VELOCITY
    cur_speed_axis = plt.subplot2grid(shape=(20, 4), loc=(10, 0), colspan=(1), rowspan=(1))
    cur_speed_axis.set_title('speed (km / h)', fontsize=12)
    cur_speed_axis.set_xlim([-2, 2])   
    cur_speed_axis.set_ylim([-2, 2])
    cur_speed_axis.set_xticks([])  
    cur_speed_axis.set_yticks([])  


    # LAP TIME PLOT
    lap_time_axis = plt.subplot2grid(shape=(20,4), loc=(8,3), colspan=(1), rowspan=(1))
    lap_time_axis.set_title('time (s)', fontsize=12)
    lap_time_axis.set_xlim(-4, 4)
    lap_time_axis.set_ylim(-2, 2)
    lap_time_axis.set_xticks([])
    lap_time_axis.set_yticks([])


    # THROTTLE PLOT
    throttle_axis = plt.subplot2grid(shape=(2, 4), loc=(1,2), colspan=(1), rowspan=(1))
    throttle_axis.set_ylim(0, 110)
    throttle_axis.set_xlim(-1, 1)
    # throttle_axis.set_xticks([])
    # throttle_axis.set_yticks([])


    # GEAR PLOT
    gear_axis = plt.subplot2grid(shape=(20, 4), loc=(11,3), colspan=(1), rowspan=(1))
    gear_axis.set_title('gear', fontsize=12, color='white')
    gear_axis.set_xlim(-1,1)
    gear_axis.set_ylim(-1,1)
    gear_axis.set_xticks([])
    gear_axis.set_yticks([])


    # plotting the corners of the track
    position_axis.scatter(stored_x_corners, stored_y_corners, s=2)
    # plot the track
    position_axis.plot(stored_x_pos_series, stored_y_pos_series, color='grey') 
    # plotting the movement of the car
    animated_position, = position_axis.plot([], [], color='green')


    animated_velocity, = velocity_axis.plot([], [], color='red')

    animated_cr_speed = cur_speed_axis.text(0, 0, s='', ha='center', va='center', fontsize=15)

    animated_throttle, = throttle_axis.bar(['Throttle'], [0], color='green')  # reference to rectangle

    animated_lap_time = lap_time_axis.text(0, 0, s='', ha='center', va='center', fontsize=15)

    animated_gear = gear_axis.text(0, 0, s='', ha='center', va='center', fontsize=15)


    def update_data(frame):
        # POSITION
        x = stored_x_pos_series[:frame]
        y = stored_y_pos_series[:frame]
        animated_position.set_data((x, y))

        # VELOCITY
        t = stored_time_series[:frame]
        s = stored_velocity_series[:frame]
        animated_velocity.set_data((t, s))

        # CURRENT SPEED
        cur_speed = round(stored_velocity_series.iloc[frame], 1)
        animated_cr_speed.set_text(cur_speed)       # set_text automatically convert to str

        # LAP TIME
        lt = str(stored_time_series.iloc[frame])
        animated_lap_time.set_text(lt)

        # THROTTLE
        thr = stored_throttle_series.iloc[frame]
        if thr < 20: 
            thr_color = 'yellow'
        elif thr < 50:
            thr_color = 'orange'
        else: 
            thr_color = 'red'
        animated_throttle.set(height=thr, color=thr_color)

        # GEAR
        gr = stored_gear_series.iloc[frame]
        animated_gear.set_text(gr)

        if frame > 0 and frame != last_item_index:
            if gr != stored_gear_series.iloc[frame + 1]:
                gear_axis.set_facecolor('#FFFEF7')
                animated_gear.set_color('#1e1c1b')

            elif gr != stored_gear_series.iloc[frame - 1]:
                gear_axis.set_facecolor('#1e1c1b')
                animated_gear.set_color('#FFFEF7')

            else:
                gear_axis.set_facecolor('#1e1c1b')
                animated_gear.set_color('#FFFEF7')
                

        elif frame == 0:
            gear_axis.set_facecolor('#1e1c1b')
            animated_gear.set_color('#FFFEF7')


        else:
            gear_axis.set_facecolor('#1e1c1b')
            animated_gear.set_color('#FFFEF7')

        return (animated_position), (animated_velocity), (animated_cr_speed), (animated_lap_time), (animated_throttle), (animated_gear), (gear_axis)
        

    # initialize animation parameters
    p_frame = len(stored_x_pos_series)
    last_item_index = p_frame - 1
    p_intv =  stored_lap_time_in_ms / float(p_frame)

    
    animation = FuncAnimation(
        fig = fig,
        func=update_data,
        frames=p_frame,         
        interval=p_intv,
        blit=True
    )

    # show animation
    plt.show()

def main():
    
    stored_year, stored_gp, stored_driver, stored_session = initialize_session()

    print(type(stored_session))

    stored_fastest_lap, stored_lap_time_in_s, stored_lap_time_in_ms, stored_time_series, stored_x_pos_series, stored_y_pos_series, stored_velocity_series, stored_gear_series, stored_throttle_series, stored_x_corners, stored_y_corners = get_data(stored_driver, stored_session)

    stored_fast_x_min, stored_fast_x_max, stored_fast_y_min, stored_fast_y_max = track_plot_limit(stored_fastest_lap)

    animation_plot(stored_driver, stored_gp, stored_year, stored_fastest_lap, stored_lap_time_in_s, stored_lap_time_in_ms, stored_time_series, stored_x_pos_series, stored_y_pos_series, stored_velocity_series, stored_gear_series, stored_throttle_series, stored_x_corners, stored_y_corners, stored_fast_x_min, stored_fast_x_max, stored_fast_y_min, stored_fast_y_max)
    
main()
