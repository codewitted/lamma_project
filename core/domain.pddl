(define (domain lamma_p_domain)
  (:requirements :strips :typing :negative-preconditions)
  (:types
    object
    location
    robot - location
  )

  (:predicates
    (at ?obj - object ?loc - location)
    (on ?obj - object ?loc - location)
    (inside ?obj - object ?container - object)
    (holding ?obj - object)
    (opened ?obj - object)
    (closed ?obj - object)
    (switchedOn ?obj - object)
    (switchedOff ?obj - object)
    (is_openable ?obj - object)
    (is_toggleable ?obj - object)
  )

  (:action move_to
    :parameters (?r - robot ?from - location ?to - location)
    :precondition (at ?r ?from)
    :effect (and (at ?r ?to) (not (at ?r ?from))))

  (:action pick_up
    :parameters (?obj - object ?loc - location)
    :precondition (and (at fetch_robot ?loc) (at ?obj ?loc) (not (holding something))) ; something is a simplification
    :effect (and (holding ?obj) (not (at ?obj ?loc))))

  (:action open
    :parameters (?obj - object)
    :precondition (and (at fetch_robot ?obj) (is_openable ?obj) (closed ?obj))
    :effect (and (opened ?obj) (not (closed ?obj))))

  (:action close
    :parameters (?obj - object)
    :precondition (and (at fetch_robot ?obj) (is_openable ?obj) (opened ?obj))
    :effect (and (closed ?obj) (not (opened ?obj))))

  (:action switch_on
    :parameters (?obj - object)
    :precondition (and (at fetch_robot ?obj) (is_toggleable ?obj) (switchedOff ?obj))
    :effect (and (switchedOn ?obj) (not (switchedOff ?obj))))

  (:action switch_off
    :parameters (?obj - object)
    :precondition (and (at fetch_robot ?obj) (is_toggleable ?obj) (switchedOn ?obj))
    :effect (and (switchedOff ?obj) (not (switchedOn ?obj))))
)
