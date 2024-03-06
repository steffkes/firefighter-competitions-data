import { count as countRecbbcQl0KFKj7Ox4 } from "./server/api/competitions/recbbcQl0KFKj7Ox4.json.js";
import { count as countRecNdFl6cR1xA5l4p } from "./server/api/competitions/recNdFl6cR1xA5l4p.json.js";
import { count as countRecqjh5V3DUAzgLYQ } from "./server/api/competitions/recqjh5V3DUAzgLYQ.json.js";
import { count as countRecRqH7LW1AQQ66FR } from "./server/api/competitions/recRqH7LW1AQQ66FR.json.js";
import { count as countRecVzAj3TgO0th7JC } from "./server/api/competitions/recVzAj3TgO0th7JC.json.js";
import { count as countRecxAxWccPrMWcVVv } from "./server/api/competitions/recxAxWccPrMWcVVv.json.js";
import { count as countRecyC5LmxecehTxWD } from "./server/api/competitions/recyC5LmxecehTxWD.json.js";

const data = {
  recbbcQl0KFKj7Ox4: await countRecbbcQl0KFKj7Ox4(),
  recNdFl6cR1xA5l4p: await countRecNdFl6cR1xA5l4p(),
  recqjh5V3DUAzgLYQ: await countRecqjh5V3DUAzgLYQ(),
  recRqH7LW1AQQ66FR: await countRecRqH7LW1AQQ66FR(),
  recVzAj3TgO0th7JC: await countRecVzAj3TgO0th7JC(),
  recxAxWccPrMWcVVv: await countRecxAxWccPrMWcVVv(),
  recyC5LmxecehTxWD: await countRecyC5LmxecehTxWD(),
};

const date = new Date();
const str = (object) => JSON.stringify({ date: date.toISOString(), ...object });

for (const [competition, count] of Object.entries(data)) {
  console.log(str({ competition, count }));
}
