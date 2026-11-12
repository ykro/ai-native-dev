import type { TravelPlan } from "../schemas";

export const VALID_ITINERARY_FIXTURE: TravelPlan = {
  intro: "Tres días entre arquitectura colonial, cafetales y volcanes en Antigua Guatemala.",
  days: [
    {
      day: 1,
      title: "Centro histórico y conventos",
      activities: ["Arco de Santa Catalina", "Ruinas de la Catedral", "Convento de Capuchinas"],
    },
    {
      day: 2,
      title: "Volcanes y miradores",
      activities: ["Ascenso matutino al Volcán Pacaya", "Mirador del Cerro de la Cruz"],
    },
    {
      day: 3,
      title: "Ruta del café y gastronomía",
      activities: ["Finca cafetalera en San Miguel Escobar", "Mercado de artesanías del Carmen"],
    },
  ],
  hiddenGem: {
    title: "San Juan del Obispo",
    description: "Pueblo tranquilo al pie del Volcán de Agua famoso por su níspero y chocolate artesanal.",
  },
  localFood: {
    dish: "Pepián antigüeño",
    description: "Recado tradicional de semillas tostadas, chiles secos y especias servido con arroz.",
  },
};
