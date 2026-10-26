; Mission 1. Fixed landing site selection: wp1.
; Only arrows shown in the assignment map appear as connected facts.
; Unspecified atoms are initially false (closed-world assumption).
(define (problem lunar-mission-1)
  (:domain lunar)
  (:objects
    rover1 - rover
    lander1 - lander
    wp1 wp2 wp3 wp4 wp5 - waypoint
  )
  (:init
    (belongs-to rover1 lander1)
    (lander-at lander1 wp1)
    (aboard rover1 lander1)
    (data-free rover1)
    (sample-free rover1)
    (lander-sample-free lander1)
    (connected wp1 wp2)
    (connected wp2 wp3)
    (connected wp3 wp5)
    (connected wp5 wp1)
    (connected wp1 wp4)
    (connected wp4 wp3)
  )
  (:goal (and
    (image-saved lander1 wp5)
    (scan-saved lander1 wp3)
    (sample-stored lander1 wp1)
  ))
)
