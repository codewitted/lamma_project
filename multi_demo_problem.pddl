(define (problem robotics_task)
  (:domain lamma_p_domain)
  (:objects
    limo_heavy1 limo_scout1 - robot
    unknown red_block floor2_lab_workbench floor6_hallway - target
  )
  (:init
    (at red_block floor6_hallway)
    (at limo_scout1 unknown)
    (at limo_heavy1 floor6_hallway)
    (can_manipulate limo_heavy1)
    (can_sense limo_scout1)
  )
  (:goal
    (and
      (at red_block floor2_lab_workbench)
    )
  )
)
