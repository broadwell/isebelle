/**
 * Clamps a number between a minimum and maximum value.
 *
 * @param {number} num - The number to clamp.
 * @param {number} min - The minimum value.
 * @param {number} max - The maximum value.
 * @return {number} The clamped number.
 */
export const clamp = (num, min, max) => (num < min ? min : num > max ? max : num);

/**
 * Gets the mean of an array.
 *
 * @param {[number]} arr - The array.
 * @return {number} The mean.
 */
export const mean = arr => arr.reduce((a, b) => a + b) / arr.length;

/**
 * Gets the median value of an array.
 *
 * @param {[number]} arr - The array.
 * @return {number} The median.
 */
export const median = (arr) => {
  if (!arr.length) return 0;
  const s = [...arr].sort((a, b) => a - b);
  const mid = Math.floor(s.length / 2);
  return s.length % 2 ? s[mid] : ((s[mid - 1] + s[mid]) / 2);
}


/**
 * Gets the mode value of an array.
 *
 * @param {[number]} arr - The array.
 * @return {number} The mode.
 */
export const mode = (arr) => {
  if (!arr.length) return 0;
  let freqs = {};
  let maxFreq = 0;
  let maxItem = 0;
  arr.forEach((rawItem) => {
    const item = Math.round(rawItem);
    if (item in Object.keys(freqs)) {
      freqs[item] += 1;
    } else {
      freqs[item] = 1;
    }
    if (freqs[item] > maxFreq) {
      maxItem = item;
      maxFreq = freqs[item];
    }
  });
  return maxItem;
}