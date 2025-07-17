//MobFactory.h
/*
Copyright (C) 2004  Anders Hedstrom

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
*/

#ifndef _MOBFACTORY_H
#define _MOBFACTORY_H

#include <string>
#include <vector>
#include "SmallHandler.h"

class SmallSocket;

/** Contains/spawns mobiles/npcs. */
class MobFactory
{
	/** Mobile/NPC properties struct. */
	struct MOB
	{
		MOB(SmallHandler& handler,int x,int y,const std::string& name) : m_handler(handler),m_x(x),m_y(y),m_name(name) {
		}
		void Move();
		void Create();
		void SetNewPos(int,int);
		//
		SmallHandler& m_handler;
		int m_x;
		int m_y;
		std::string m_name;
	};
	typedef std::vector<MOB *> mob_v;
public:
	MobFactory(SmallHandler& w);
	~MobFactory();

	void Spawn();
	void RandomAction();
	void ShowNamesAt(SmallSocket *,int x,int y,const std::string& = "");
	SmallHandler& Handler() { return m_handler; }
	size_t NumberOfMobs() { return m_mobs.size(); }

private:
	SmallHandler& m_handler;
	mob_v m_mobs;
	string_v m_name_beg;
	string_v m_name_end;
};




#endif // _MOBFACTORY_H
