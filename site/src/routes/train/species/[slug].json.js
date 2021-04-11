import path from 'path';
import fs from 'fs';

const DATA_DIR = '../data';

export async function get({ params }) {
	const { slug } = params;
	let examples = fs.readdirSync(path.join(DATA_DIR, '/motif/train_short_audio', slug));
	return {
		body: JSON.stringify(examples)
	};
}
