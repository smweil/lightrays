def draw_rotating_tri_fractals(frame,window,pts,polygon_list, color = (0,255,0),
tail_length=255, dbg=0):
    '''
    Points are the center points of the triangle to be drawn
    Count is the running iteration count of the program -1 means that no
    staicking will occur
    tail_length is the length of the desired tail
    tail_stack is the amount of frames to stack up giving the blur effect
    '''
    height = frame.shape[0]
    width = frame.shape[1]

    #check if the buffer is smaller than the number of points:
    if tail_length > len(pts):
        #set the tail length to the number of points we have:
        tail_length = len(pts)

    color_flag = 1

    for i in range(1, tail_length):
        if pts[i] is None:
            continue

        tri_pts = tri_from_center(pts[i],height=20,rotation=i*2,scale=1)
        color = hsv2rgb((i)/360,1,1)
        cv2.polylines(frame,[tri_pts],True,color,3,lineType=cv2.LINE_AA)
        polygon_list.appendleft(tri_pts)

        #Draw on tails:
        if tail_length > 0 and i > int(tail_length/2):
            cv2.polylines(frame,[tri_pts],True,(0,0,0),1,lineType=cv2.LINE_AA)

        #add fractals
        for corner in tri_pts:
            tri_corner = tri_from_center(corner,height=20,rotation=i*4,scale=1)
            if color_flag: #display colors!
                #hue_modifier = int((LaserTracker.disDeque[i]**4)*2)
                # hue_modifier = LaserTracker.upperRange[0]
                color = hsv2rgb((i+50)/360,1,1)
                cv2.polylines(frame,[tri_corner],True,color,1,lineType=cv2.LINE_AA)
                #add triangle points to the returned list

            #This is where we color the tails or erase the tail:
            #If tail_length < 0 we dont do anything (-1 flag)

            # cv2.polylines(frame,[tri_corner],True,(0,0,0),1,lineType=cv2.LINE_AA)

    cv2.imshow(window, frame)
