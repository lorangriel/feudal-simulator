#ifndef _item_H
#define _item_H

#include <vector>
#include <string>

/* equipment slots */
typedef enum : char {
  slot_head = 'A',
  slot_ear,
  slot_nose,
  slot_upper_lip,
  slot_lower_lip,
  slot_shoulder,
  slot_upper_arm,
  slot_lower_arm,
  slot_hand,
  slot_thumb,
  slot_index_finger,
  slot_middle_finger,
  slot_ring_finger,
  slot_pinky,
  slot_neck,
  slot_throat,
  slot_chest,
  slot_back,
  slot_hip,
  slot_crotch,
  slot_upper_leg,
  slot_lower_leg,
  slot_foot,
  slot_big_toe,
  slot_2nd_toe,
  slot_3rd_toe,
  slot_4th_toe,
  slot_5th_toe,
  slot_waist,
  slot_lower_body,
  slot_ankle,
  slot_wrist,
  slot_forehead,
  slot_cheek,
  slot_chin,
  slot_upper_body,
  slot_mouth,
  slot_nostril,
  slot_shoulderblade,
  slot_shoulders,
} slot_t;
const std::vector<char> slot_types = {
  slot_head, slot_ear, slot_nose, slot_upper_lip, slot_lower_lip, slot_shoulder, slot_upper_arm, slot_lower_arm,
  slot_hand, slot_thumb, slot_index_finger, slot_middle_finger, slot_ring_finger, slot_pinky, slot_neck, slot_throat,
  slot_chest, slot_back, slot_hip, slot_crotch, slot_upper_leg, slot_lower_leg, slot_foot, slot_big_toe,
  slot_2nd_toe, slot_3rd_toe, slot_4th_toe, slot_5th_toe, slot_waist, slot_lower_body, slot_ankle, slot_wrist,
  slot_forehead, slot_cheek, slot_chin, slot_upper_body, slot_mouth, slot_nostril, slot_shoulderblade, slot_shoulders };
const std::vector<std::string> slot_names = {
  "head", "ear", "nose", "upper lip", "lower lip", "shoulder", "upper arm", "lower arm",
  "hand", "thumb", "index finger", "middle finger", "ring finger", "pinky", "neck", "throat",
  "chest", "back", "hip", "crotch", "upper leg", "lower leg", "foot", "big toe",
  "second toe", "third toe", "fourth toe", "fifth toe", "waist", "lower body", "ankle", "wrist",
  "forehead", "cheek", "chin", "upper body", "mouth", "nostril", "shoulderblade", "shoulders" };
const std::vector<bool> slot_lr = {
  0, 1, 0, 1, 1, 1, 1, 1,
  1, 1, 1, 1, 1, 1, 0, 0,
  0, 0, 1, 0, 1, 1, 1, 1,
  1, 1, 1, 1, 0, 0, 1, 1,
  0, 1, 0, 0, 0, 1, 1, 0 };
const std::vector<std::string> slot_item = {
  "helmet", "earring", "nose ring", "lip piercing", "lip piercing", "shoulder pad", "upper arm protection", "lower arm protection",
  "gauntlet", "ring", "ring", "ring", "ring", "ring", "neck protection", "necklace",
  "", "", "pouch", "crotch protection", "upper leg protection", "lower leg protection", "shoe", "ring",
  "ring", "ring", "ring", "ring", "belt", "lower body protection", "bracelet", "bracelet",
  "", "", "", "upper body protection", "mouth cover", "piercing", "quiver", "backpack" };
const std::vector<bool> slot_armor = {
  1, 0, 0, 0, 0, 1, 1, 1,
  1, 0, 0, 0, 0, 0, 1, 0,
  0, 0, 0, 1, 1, 1, 1, 0,
  0, 0, 0, 0, 0, 1, 0, 0,
  0, 0, 0, 1, 0, 0, 0, 0 };
const std::vector<bool> slot_additional_clothing = {
  1, 0, 1, 0, 0, 0, 0, 0,
  1, 0, 0, 0, 0, 0, 1, 0,
  0, 1, 0, 0, 0, 0, 0, 0,
  0, 0, 0, 0, 0, 1, 0, 0,
  0, 0, 0, 1, 0, 0, 0, 0 };
const std::vector<std::string> clothing_types = {
  "hat", "", "nose cap", "", "", "", "", "",
  "glove", "", "", "", "", "", "scarf", "",
  "", "cloak", "", "", "", "", "", "",
  "", "", "", "", "", "pair of trousers", "", "",
  "", "", "", "shirt", "", "", "", "" };
const std::vector<bool> slot_tattoo = {
  0, 0, 0, 0, 0, 0, 1, 1,
  1, 0, 0, 0, 0, 0, 1, 0,
  1, 1, 0, 0, 1, 1, 1, 0,
  0, 0, 0, 0, 0, 0, 1, 1,
  1, 1, 0, 0, 0, 0, 0, 0 };
/* weapon */
typedef enum : char {
  damage_delivery_melee = 'A',
  damage_delivery_projectile,
  damage_delivery_beam,
} damage_delivery_t;
const std::vector<char> damage_delivery_types = {
  damage_delivery_melee, damage_delivery_projectile, damage_delivery_beam };
const std::vector<std::string> damage_delivery_names = {
  "melee", "projectile", "beam" };
typedef enum : char {
  damage_kinetic = 'A',
  damage_electric,
  damage_magnetic,
  damage_particle,
  damage_laser,
  damage_sound,
  damage_elemental,
  damage_dark,
  damage_fire,
  damage_ice,
  damage_magic,
  damage_mental,
} damage_t;
const std::vector<char> damage_types = {
  damage_kinetic,
  damage_electric, damage_magnetic, damage_particle, damage_laser, damage_sound,
  damage_elemental,
  damage_dark, damage_fire, damage_ice, damage_magic, damage_mental };
const std::vector<std::string> damage_names = {
  "kinetic",
  "electric", "magnetic", "particle", "laser", "sound",
  "elemental",
  "dark", "fire", "ice", "magic", "mental" };

#endif // _item_H
