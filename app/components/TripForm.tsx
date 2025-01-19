import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

export default function TripForm({ onSubmit }) {
  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <div>
        <Label htmlFor="startPoint">Starting Point</Label>
        <Input type="text" id="startPoint" name="startPoint" required />
      </div>
      <div>
        <Label htmlFor="destination">Destination</Label>
        <Input type="text" id="destination" name="destination" required />
      </div>
      <div>
        <Label htmlFor="numStops">Number of Stops</Label>
        <Input type="number" id="numStops" name="numStops" min="1" required />
      </div>
      <div>
        <Label htmlFor="availableTime">Available Time (hours)</Label>
        <Input type="number" id="availableTime" name="availableTime" min="1" required />
      </div>
      <Button type="submit">Plan My Trip</Button>
    </form>
  )
}

