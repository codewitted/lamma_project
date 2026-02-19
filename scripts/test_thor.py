import ai2thor.controller
import os

def test():
    try:
        controller = ai2thor.controller.Controller(
            scene="FloorPlan1",
            agentMode="default",
            visibilityDistance=2.0,
            gridSize=0.25,
            width=300,
            height=300
        )
        event = controller.step(action="RotateRight")
        print("✅ AI2-THOR initialized and stepped successfully.")
        # Save a frame to verify rendering
        import PIL.Image
        img = PIL.Image.fromarray(event.frame)
        img.save("thor_test_frame.png")
        print("✅ Frame saved as thor_test_frame.png")
        controller.stop()
    except Exception as e:
        print(f"❌ AI2-THOR failed: {e}")

if __name__ == "__main__":
    test()
