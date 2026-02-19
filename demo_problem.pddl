(define (problem robotics_task)
  (:domain lamma_p_domain)
  (:objects
    robot1 - robot
    floor_6_hallway floor_2_lab floor6_charging_dock workbench red_block - target
  )
  (:init
    (at red_block floor_6_hallway)
    (at robot1 floor6_charging_dock)
  )
  (:goal
    (and
      (at red_block workbench)
    )
  )
)
