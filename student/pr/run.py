# import audio
# import head_pose
# import detection

import asyncio
import threading as th

from student.pr import audio
from student.pr import head_pose
from student.pr import detection

# def cam():
# # if __name__ == "__main__":
#     # main()
#     head_pose_thread = th.Thread(target=head_pose.pose)
#     audio_thread = th.Thread(target=audio.sound)
#     detection_thread = th.Thread(target=detection.run_detection)

#     head_pose_thread.start()
#     audio_thread.start()
#     detection_thread.start()

#     head_pose_thread.join()
#     audio_thread.join()
#     detection_thread.join()



async def cam():
# if __name__ == "__main__":
    # main()
    await asyncio.sleep(1)
    head_pose_thread = th.Thread(target=head_pose.pose)
    audio_thread = th.Thread(target=audio.sound)
    detection_thread = th.Thread(target=detection.run_detection)

    head_pose_thread.start()
    audio_thread.start()
    detection_thread.start()

    head_pose_thread.join()
    audio_thread.join()
    detection_thread.join()
    print("Cam function executed asynchronously")


# async def cam():
#     # Your cam function logic here
#     await asyncio.sleep(1)  # Example asynchronous operation

#     # Example: Print a message after waiting
#     print("Cam function executed asynchronously")

# # Now you can await run.cam() in an async context
