#include "item.h"

#include <iostream>
#include <sstream>

#include <cstring>

static bool html( false );

std::string col(const std::string& txt, const std::string& background, const std::string& fgcolor)
{
  if (!html)
    return txt;
  std::ostringstream str;
  str << "<font style=\"";
  if (!background.empty())
    str << " background: " << background << ";";
  if (!fgcolor.empty())
    str << " color: " << fgcolor << ";";
  str << "\">" << txt << "</font>";
  return str.str();
}

int main(int argc, char *argv[])
{
  std::string title_bg( "black" );
  std::string title_color( "white" );
  std::string name_bg( "black" );
  std::string name_color( "#00ee00" );
  std::string item_bg( "black" );
  std::string item_color( "#333333" );
  std::string cloth_bg( "black" );
  std::string cloth_color( "gold" );
  std::string tat_bg( "black" );
  std::string tat_color( "red" );
  for (int i(1); i < argc; i++)
    if (!strcmp(argv[i], "-html"))
      html = true;
  if (html)
    std::cout << "<html><head><title>eq.txt</title></head><body style=\"background: black; color: green;\">";
  for (int i(0); i < 2; i++)
  {
    bool armor( i == 0 );
    if (html)
      std::cout << "<h3>";
    std::cout << col((armor ? "Armor" : "Equipment"), title_bg, title_color) << std::endl;
    if (html)
      std::cout << "</h3>";
    else
      std::cout << "---------" << std::endl;
    if (html)
      std::cout << "<ul>";
    for (size_t i(0); i < slot_types.size(); i++)
    {
      if (armor ^ slot_armor[i])
        continue;
      char t( slot_types[i] );
      std::string name( slot_names[i] );
      bool lr( slot_lr[i] );
      std::string item_name( slot_item[i] );
      std::string clothing( clothing_types[i] );
      std::string tmp( "  [" + col(std::string(&t, 1), title_bg, title_color) + "] " );
      bool tat( slot_tattoo[i] );
      if (lr)
        tmp += "Your right and left " + col(name, name_bg, name_color) + " ";
      else
        tmp += "Your " + col(name, name_bg, name_color) + " ";
      if (html)
        std::cout << "<li>";
      if (!item_name.empty())
      {
        std::string eq( armor ? "equip" : "wear" );
        std::cout << tmp << "may " << eq << " " << col("one " + item_name, item_bg, item_color);
        if (lr)
          std::cout << " each";
        tmp = ", and ";
      }
      if (!clothing.empty())
      {
        std::cout << tmp << "is able to wear " << col("one " + clothing, cloth_bg, cloth_color);
        if (lr)
          std::cout << " each";
        tmp = ", and ";
      }
      if (tat)
      {
        std::cout << tmp << "can be " << col("tattooed", tat_bg, tat_color);
        tmp = ", and ";
      }
      if (tmp != ", and ")
      {
        std::cout << tmp << "just sits there";
        tmp = ", and ";
      }
      std::cout << "." << std::endl;
      if (html)
        std::cout << "</li>";
    }
    if (html)
      std::cout << "</ul>";
    std::cout << std::endl;
  }
  /* */
  if (html)
    std::cout << "<h3>";
  std::cout << col("Damage", title_bg, title_color) << std::endl;
  if (html)
    std::cout << "</h3>";
  else
    std::cout << "---------" << std::endl;
  if (html)
    std::cout << "<ul>";
  for (size_t i(0); i < damage_types.size(); i++)
  {
    char t( damage_types[i] );
    if (html)
      std::cout << "<li>";
    std::string name( damage_names[i] );
    std::cout << "  [" << col(std::string(&t, 1), title_bg, title_color) << "]";
    std::cout << " " << col(name, name_bg, name_color);
    std::cout << std::endl;
    if (html)
      std::cout << "</li>";
  }
  if (html)
    std::cout << "</ul>";
  std::cout << std::endl;
  /* */
  if (html)
    std::cout << "<h3>";
  std::cout << col("Damage Delivery", title_bg, title_color) << std::endl;
  if (html)
    std::cout << "</h3>";
  else
    std::cout << "---------" << std::endl;
  if (html)
    std::cout << "<ul>";
  for (size_t i(0); i < damage_delivery_types.size(); i++)
  {
    char t( damage_delivery_types[i] );
    if (html)
      std::cout << "<li>";
    std::string name( damage_delivery_names[i] );
    std::cout << "  [" << col(std::string(&t, 1), title_bg, title_color) << "]";
    std::cout << " " << col(name, name_bg, name_color);
    std::cout << std::endl;
    if (html)
      std::cout << "</li>";
  }
  if (html)
    std::cout << "</ul>";
  //
  if (html)
    std::cout << "</body></html>" << std::endl;
}
