import path from 'path';
import fs from 'fs';

const DATA_DIR = '../data';

export async function get() {
	let species = fs.readdirSync(path.join(DATA_DIR, '/motif/train_short_audio'));
	return {
		body: JSON.stringify(species)
	};
}
