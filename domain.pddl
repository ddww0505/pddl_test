(define (domain tokyo_trip)
  (:requirements :strips :typing :action-costs)
  (:types
    day location time_slot
  )
  (:predicates
    (at ?loc - location)
    (available ?loc - location)
    (visited ?loc - location)
    (day_now ?d - day)
    (next_day ?d1 ?d2 - day)
    (time_slot_now ?ts - time_slot)
    (next_slot ?ts1 ?ts2 - time_slot)
    (open ?loc - location ?d - day ?ts - time_slot)
  )
  (:functions
    (total-cost - number)
    (travel_time ?from - location ?to - location)
    (play_time ?loc - location)
  )
  (:action move
    :parameters (?from - location ?to - location ?d - day ?ts - time_slot)
    :precondition (and
      (at ?from)
      (available ?to)
      (day_now ?d)
      (time_slot_now ?ts)
      (open ?to ?d ?ts)
    )
    :effect (and
      (not (at ?from))
      (at ?to)
      (increase (total-cost) (travel_time ?from ?to))
    )
  )
  (:action visit
    :parameters (?loc - location ?d - day ?ts - time_slot)
    :precondition (and
      (at ?loc)
      (available ?loc)
      (day_now ?d)
      (time_slot_now ?ts)
      (open ?loc ?d ?ts)
    )
    :effect (and
      (visited ?loc)
      (increase (total-cost) (play_time ?loc))
    )
  )
  (:action advance_slot
    :parameters (?ts1 - time_slot ?ts2 - time_slot ?d - day)
    :precondition (and
      (time_slot_now ?ts1)
      (day_now ?d)
      (next_slot ?ts1 ?ts2)
    )
    :effect (and
      (not (time_slot_now ?ts1))
      (time_slot_now ?ts2)
      (increase (total-cost) 0)
    )
  )
)
