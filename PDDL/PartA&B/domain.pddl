; F29AI Part 2: lunar rover domain. STRIPS + typing only.
; Every action is generic: no mission-specific rover, lander or waypoint names.
(define (domain lunar)
  (:requirements :strips :typing)
  (:types rover lander waypoint)
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
  )

  ; Deploy a rover only from its own lander, at the fixed landing site.
  (:action deploy
    :parameters (?r - rover ?l - lander ?w - waypoint )
    :precondition (and
      (belongs-to ?r ?l)
      (aboard ?r ?l)
      (lander-at ?l ?w)
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
    :parameters (?r - rover ?l - lander ?w - waypoint )
    :precondition (and
      (belongs-to ?r ?l)
      (has-image ?r ?w)
    )
    :effect (and
      (image-saved ?l ?w)
      (data-free ?r)
      (not (has-image ?r ?w))
    )
  )

  (:action transmit-scan
    :parameters (?r - rover ?l - lander ?w - waypoint )
    :precondition (and
      (belongs-to ?r ?l)
      (has-scan ?r ?w)
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
    :parameters (?r - rover ?l - lander ?source - waypoint ?site - waypoint )
    :precondition (and
      (belongs-to ?r ?l)
      (rover-at ?r ?site)
      (lander-at ?l ?site)
      (has-sample ?r ?source)
      (lander-sample-free ?l)
    )
    :effect (and
      (sample-stored ?l ?source)
      (sample-free ?r)
      (not (has-sample ?r ?source))
      (not (lander-sample-free ?l))
    )
  )
)
