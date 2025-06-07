/**
 * Clamps a number between a minimum and maximum value.
 *
 * @param {number} num - The number to clamp.
 * @param {number} min - The minimum value.
 * @param {number} max - The maximum value.
 * @return {number} The clamped number.
 */
export const clamp = (num, min, max) => (num < min ? min : num > max ? max : num);
