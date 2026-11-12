import { describe, expect, it } from 'vitest';
import pets from './pets.json';

describe('pets.json', () => {
  it('has pets with id, name and a three-line bio', () => {
    expect(pets.length).toBeGreaterThan(0);
    for (const pet of pets) {
      expect(Number.isInteger(pet.id)).toBe(true);
      expect(pet.name.length).toBeGreaterThan(0);
      expect(pet.bio.split('\n')).toHaveLength(3);
    }
  });
});
