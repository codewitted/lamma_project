(define (domain lamma_p_domain)
  (:requirements :strips :typing :negative-preconditions)
  (:types
    target - object
    location object_type - target
    robot - object_type
  )

  (:predicates
    (at ?obj - target ?loc - target)
    (on ?obj - target ?loc - target)
    (inside ?obj - target ?container - target)
    (holding ?r - robot ?obj - target)
    (opened ?obj - target)
    (closed ?obj - target)
    (switchedOn ?obj - target)
    (switchedOff ?obj - target)
    (is_openable ?obj - target)
    (is_toggleable ?obj - target)
  )

  (:action move_to
    :parameters (?r - robot ?from - target ?to - target)
    :precondition (at ?r ?from)
    :effect (and (at ?r ?to) (not (at ?r ?from))))

  (:action pick_up
    :parameters (?r - robot ?obj - target ?loc - target)
    :precondition (and (at ?r ?loc) (at ?obj ?loc) (not (holding ?r ?obj))) ; simplified check
    :effect (and (holding ?r ?obj) (not (at ?obj ?loc))))

  (:action open
    :parameters (?r - robot ?obj - target)
    :precondition (and (at ?r ?obj) (is_openable ?obj) (closed ?obj))
    :effect (and (opened ?obj) (not (closed ?obj))))

  (:action close
    :parameters (?r - robot ?obj - target)
    :precondition (and (at ?r ?obj) (is_openable ?obj) (opened ?obj))
    :effect (and (closed ?obj) (not (opened ?obj))))

  (:action switch_on
    :parameters (?r - robot ?obj - target)
    :precondition (and (at ?r ?obj) (is_toggleable ?obj) (switchedOff ?obj))
    :effect (and (switchedOn ?obj) (not (switchedOff ?obj))))

  (:action switch_off
    :parameters (?r - robot ?obj - target)
    :precondition (and (at ?r ?obj) (is_toggleable ?obj) (switchedOn ?obj))
    :effect (and (switchedOff ?obj) (not (switchedOn ?obj))))

  (:action place
    :parameters (?r - robot ?obj - target ?loc - target)
    :precondition (and (at ?r ?loc) (holding ?r ?obj))
    :effect (and (at ?obj ?loc) (not (holding ?r ?obj))))

  (:action drop
    :parameters (?r - robot ?obj - target ?loc - target)
    :precondition (and (at ?r ?loc) (holding ?r ?obj))
    :effect (and (at ?obj ?loc) (not (holding ?r ?obj))))
)
