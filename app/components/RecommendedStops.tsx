import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function RecommendedStops({ stops }) {
  return (
    <div className="mt-8">
      <h2 className="text-2xl font-bold mb-4">Recommended Stops</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {stops.map((stop, index) => (
          <Card key={index}>
            <CardHeader>
              <CardTitle>{stop.name}</CardTitle>
            </CardHeader>
            <CardContent>
              <p>Rating: {stop.rating} / 5</p>
              <p>Recommended Time: {stop.recommendedTime} hours</p>
              <p>Reviews: {stop.reviews}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

