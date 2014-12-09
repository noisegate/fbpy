#test drawing while keeping background...
import fbpy.fb as fb
import time

if __name__ == "__main__":
    main = fb.Surface()

    window = fb.Surface((100,100),(400,400))

    window.store()
    
    for r in range(0,100):
        window.clear()
        window.restore()
        window.circle((0.5,0.5),r/200.0,100, fb.Colors.grey, fb.Styles.solid)
        window.update()
        time.sleep(0.01)

    fb.Surface.close()
