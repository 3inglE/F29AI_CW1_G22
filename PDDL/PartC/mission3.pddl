; Mission 3. Fixed landing site selection: wp1 for lander2; lander1 is required at wp2.
; Only arrows shown in the assignment map appear as connected facts.
; Unspecified atoms are initially false (closed-world assumption).
(define (problem lunar-mission-3)
  (:domain lunar-extended)
  (:objects
    rover1 rover2 - rover
    lander1 lander2 - lander
    wp1 wp2 wp3 wp4 wp5 wp6 - waypoint
    alice bob - astronaut
  )
  (:init
    (belongs-to rover1 lander1)
    (belongs-to rover2 lander2)
    (lander-at lander1 wp2)
    (lander-at lander2 wp1)
    (rover-at rover1 wp2)
    (aboard rover2 lander2)
    (data-free rover1)
    (data-free rover2)
    (sample-free rover1)
    (sample-free rover2)
    (lander-sample-free lander1)
    (lander-sample-free lander2)
    (astronaut-of alice lander1)
    (astronaut-of bob lander2)
    (in-docking-bay alice lander1)
    (in-control-room bob lander2)
    (connected wp1 wp2)
    (connected wp2 wp1)
    (connected wp2 wp3)
    (connected wp3 wp5)
    (connected wp5 wp3)
    (connected wp5 wp6)
    (connected wp6 wp4)
    (connected wp4 wp2)
    (connected wp2 wp4)
  )
  (:goal (and
    (image-saved lander1 wp3)
    (scan-saved lander2 wp4)
    (image-saved lander2 wp2)
    (scan-saved lander1 wp6)
    (sample-stored lander1 wp5)
    (sample-stored lander2 wp1)
  ))
)
