'use server'

import { z } from 'zod'
import { ChatGPTAPI } from 'chatgpt'  // Assuming 'chatgpt' is an npm package for interacting with the API

const formSchema = z.object({
  startPoint: z.string(),
  destination: z.string(),
  numStops: z.string().transform(Number),
  availableTime: z.string().transform(Number),
})

// Initialize ChatGPT API
const chatGPT = new ChatGPTAPI({ apiKey: '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' })

export async function planTrip(formData: FormData) {
  const { startPoint, destination, numStops, availableTime } = formSchema.parse(
    Object.fromEntries(formData)
  )

  const stops = await generateStopsWithChatGPT(startPoint, destination, numStops, availableTime)
  const hotels = await getHotelRecommendationsWithChatGPT(destination)

  return { stops, hotels }
}

async function generateStopsWithChatGPT(startPoint, destination, numStops, availableTime) {
  const prompt = `Generate ${numStops} stops for a trip from ${startPoint} to ${destination} within ${availableTime} hours. Provide a brief description, recommended time at each stop, and number of reviews for each stop.`

  const response = await chatGPT.sendMessage(prompt)
  const data = JSON.parse(response.message) // Assuming the response is JSON formatted

  return data.stops
}

async function getHotelRecommendationsWithChatGPT(destination) {
  const prompt = `Suggest 3 hotels in ${destination}. Provide a brief description, rating, and price for each hotel.`

  const response = await chatGPT.sendMessage(prompt)
  const data = JSON.parse(response.message) // Assuming the response is JSON formatted

  return data.hotels
}
