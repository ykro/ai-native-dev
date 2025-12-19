import { pets } from './data/mockData';

function App() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-8 bg-warm-50">
      <header className="mb-12 text-center">
        <h1 className="text-6xl font-bold text-warm-800 mb-4 tracking-tight">
          PawsMatch
        </h1>
        <p className="text-xl text-warm-600 italic">
          Finding the perfect companion for every home.
        </p>
      </header>

      <main className="w-full max-w-4xl">
        <div className="bg-white rounded-3xl shadow-xl p-12 text-center border-4 border-warm-100">
          <h2 className="text-3xl font-semibold text-friendly-700 mb-6">
            Welcome to PawsMatch
          </h2>
          <p className="text-lg text-warm-600 mb-8 max-w-2xl mx-auto leading-relaxed">
            Our mission is to connect loving families with pets in need of a home.
            Browse through our adoption list and find your new best friend today.
          </p>

          <div className="flex gap-4 justify-center">
            <button className="px-8 py-3 bg-warm-500 text-white rounded-full font-bold text-lg hover:bg-warm-600 transition-colors shadow-lg hover:shadow-xl active:scale-95 duration-200">
              Find a Pet
            </button>
            <button className="px-8 py-3 bg-friendly-500 text-white rounded-full font-bold text-lg hover:bg-friendly-600 transition-colors shadow-lg hover:shadow-xl active:scale-95 duration-200">
              Adopt a Pet
            </button>
          </div>
        </div>

        <div className="mt-12 text-center text-warm-400 text-sm">
          {pets.length} pets available for adoption
        </div>
      </main>
    </div>
  )
}

export default App
