; F29AI Part 2: lunar rover domain. STRIPS + typing only.
; Every action is generic: no mission-specific rover, lander or waypoint names.
(define (domain lunar-extended)
  (:requirements :strips :typing)
  (:types rover lander waypoint astronaut)
  (:predicates
    (belongs-to ?r - rover ?l - lander)  ; fixed rover/lander association
    (lander-at ?l - lander ?w - waypoint) ; landers never move
    (aboard ?r - rover ?l - lander)     ; undeployed rover inside its lander
    (rover-at ?r - rover ?w - waypoint) ; deployed rover location
    (connected ?from - waypoint ?to - waypoint) ; directed edge

    (data-free ?r - rover)              ; shared capacity for image OR scan
    (has-image ?r - rover ?w - waypoint)
    (has-scan ?r - rover ?w - waypoint)
    (image-saved ?l - lander ?w - waypoint)
    (scan-saved ?l - lander ?w - waypoint)

    (sample-free ?r - rover)            ; rover's single physical sample slot
    (has-sample ?r - rover ?w - waypoint)
    (lander-sample-free ?l - lander)    ; lander's single storage slot
    (sample-stored ?l - lander ?w - waypoint)
    (astronaut-of ?a - astronaut ?l - lander)
    (in-docking-bay ?a - astronaut ?l - lander)
    (in-control-room ?a - astronaut ?l - lander)
  )

  ; Deploy a rover only from its own lander, at the fixed landing site.
  (:action deploy
    :parameters (?r - rover ?l - lander ?w - waypoint ?a - astronaut )
    :precondition (and
      (belongs-to ?r ?l)
      (aboard ?r ?l)
      (lander-at ?l ?w)
      (astronaut-of ?a ?l)
      (in-docking-bay ?a ?l)
    )
    :effect (and
      (rover-at ?r ?w)
      (not (aboard ?r ?l))
    )
  )

  ; Only directed edges in the problem initial state allow travel.
  (:action move
    :parameters (?r - rover ?from - waypoint ?to - waypoint)
    :precondition (and
      (rover-at ?r ?from)
      (connected ?from ?to)
    )
    :effect (and
      (rover-at ?r ?to)
      (not (rover-at ?r ?from))
    )
  )

  ; Images and scans use the same single-slot data capacity.
  (:action take-image
    :parameters (?r - rover ?w - waypoint)
    :precondition (and
      (rover-at ?r ?w)
      (data-free ?r)
    )
    :effect (and
      (has-image ?r ?w)
      (not (data-free ?r))
    )
  )

  (:action perform-scan
    :parameters (?r - rover ?w - waypoint)
    :precondition (and
      (rover-at ?r ?w)
      (data-free ?r)
    )
    :effect (and
      (has-scan ?r ?w)
      (not (data-free ?r))
    )
  )

  ; Wireless: rover need not be co-located with the lander.
  (:action transmit-image
    :parameters (?r - rover ?l - lander ?w - waypoint ?a - astronaut )
    :precondition (and
      (belongs-to ?r ?l)
      (has-image ?r ?w)
      (astronaut-of ?a ?l)
      (in-control-room ?a ?l)
    )
    :effect (and
      (image-saved ?l ?w)
      (data-free ?r)
      (not (has-image ?r ?w))
    )
  )

  (:action transmit-scan
    :parameters (?r - rover ?l - lander ?w - waypoint ?a - astronaut )
    :precondition (and
      (belongs-to ?r ?l)
      (has-scan ?r ?w)
      (astronaut-of ?a ?l)
      (in-control-room ?a ?l)
    )
    :effect (and
      (scan-saved ?l ?w)
      (data-free ?r)
      (not (has-scan ?r ?w))
    )
  )

  ; Physical samples occupy a separate rover slot from data.
  (:action collect-sample
    :parameters (?r - rover ?w - waypoint)
    :precondition (and
      (rover-at ?r ?w)
      (sample-free ?r)
    )
    :effect (and
      (has-sample ?r ?w)
      (not (sample-free ?r))
    )
  )

  ; Samples must physically return to their own lander; storage is limited.
  (:action store-sample
    :parameters (?r - rover ?l - lander ?source - waypoint ?site - waypoint ?a - astronaut )
    :precondition (and
      (belongs-to ?r ?l)
      (rover-at ?r ?site)
      (lander-at ?l ?site)
      (has-sample ?r ?source)
      (lander-sample-free ?l)
      (astronaut-of ?a ?l)
      (in-docking-bay ?a ?l)
    )
    :effect (and
      (sample-stored ?l ?source)
      (sample-free ?r)
      (not (has-sample ?r ?source))
      (not (lander-sample-free ?l))
    )
  )

  ; Astronaut may move only inside their own lander.
  (:action go-to-control-room
    :parameters (?a - astronaut ?l - lander)
    :precondition (and
      (astronaut-of ?a ?l)
      (in-docking-bay ?a ?l)
    )
    :effect (and
      (in-control-room ?a ?l)
      (not (in-docking-bay ?a ?l))
    )
  )

  (:action go-to-docking-bay
    :parameters (?a - astronaut ?l - lander)
    :precondition (and
      (astronaut-of ?a ?l)
      (in-control-room ?a ?l)
    )
    :effect (and
      (in-docking-bay ?a ?l)
      (not (in-control-room ?a ?l))
    )
  )
)
