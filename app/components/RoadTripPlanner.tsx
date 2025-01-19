'use client'

import { useState } from 'react'
import TripForm from './TripForm'
import RecommendedStops from './RecommendedStops'
import HotelRecommendations from './HotelRecommendations'
import { planTrip } from '../actions/planTrip'

export default function RoadTripPlanner() {
  const [tripPlan, setTripPlan] = useState(null)

  const handlePlanTrip = async (formData: FormData) => {
    const plan = await planTrip(formData)
    setTripPlan(plan)
  }

  return (
    <div>
      <TripForm onSubmit={handlePlanTrip} />
      {tripPlan && (
        <>
          <RecommendedStops stops={tripPlan.stops} />
          <HotelRecommendations hotels={tripPlan.hotels} />
        </>
      )}
    </div>
  )
}

