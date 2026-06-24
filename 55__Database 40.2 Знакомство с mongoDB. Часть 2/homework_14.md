// 1. Из коллекции customers выяснить из какого города "Sven Ottlieb"
db.getCollection('customers').find({
  ContactName: 'Sven Ottlieb'
});
// City: "Aachen"

// 2. Из коллекции ich.US_Adult_Income найти возраст самого взрослого человека
db.getCollection('US_Adult_Income')
  .find({}, { _id: 0, age: 1 })
  .sort({ age: -1 });
// age: 90

// 3. Из 2 задачи выясните, сколько человек имеют такой же возраст
db.getCollection('US_Adult_Income').find(
  { age: 90 },
  { _id: 0, age: 1 }
);
// 43 человека имеют age: 90

// 4. Найти _id ObjectId документа, в котором education " IT-career-hub"
db.getCollection('US_Adult_Income').find(
  { education: ' IT-career-hub' },
  { _id: 1, education: 1 }
);
// _id ObjectId 656e13232afc911a8a7ad5e5

// 5. Выяснить количество людей в возрасте между 20 и 30 годами
db.getCollection('US_Adult_Income').find({
  age: { $gte: 20, $lte: 30 }
});
// 8915 человек