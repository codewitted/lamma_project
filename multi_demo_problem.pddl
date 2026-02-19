(define (problem robotics_task)
  (:domain lamma_p_domain)
  (:objects
    limo_scout1 limo_heavy1 - robot
    red_block floor6_hallway floor2_lab_workbench unknown - target
  )
  (:init
    (at red_block floor6_hallway)
    (at limo_scout1 unknown)
    (at limo_heavy1 unknown)
    (can_sense limo_scout1)
    (can_manipulate limo_heavy1)
  )
  (:goal
    (and
      (at red_block floor2_lab_workbench)
    )
  )
)
