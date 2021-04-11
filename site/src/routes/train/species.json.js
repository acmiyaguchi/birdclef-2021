import path from 'path';
import fs from 'fs';

const DATA_DIR = '../data'; //process.env.DATA_DIR;

export async function get() {
	let species = fs.readdirSync(path.join(DATA_DIR, '/motif/train_short_audio'));
	console.log(species);
	return {
		body: JSON.stringify(species)
	};
}
