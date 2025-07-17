//MobFactory.cpp
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

//#include <stdio.h>

#include "SmallHandler.h"
#include "SmallSocket.h"
#include "MobFactory.h"




MobFactory::MobFactory(SmallHandler& w)
:m_handler(w)
{
	m_name_beg.push_back( "naz" );
	m_name_beg.push_back( "mor" );
	m_name_beg.push_back( "gnar" );
	m_name_beg.push_back( "aahr" );
	m_name_beg.push_back( "more" );
	m_name_beg.push_back( "dark" );
	m_name_beg.push_back( "bam" );
	m_name_beg.push_back( "raab" );
	m_name_beg.push_back( "rake" );
	m_name_beg.push_back( "lor" );
	m_name_beg.push_back( "smur" );

	m_name_end.push_back( "guz" );
	m_name_end.push_back( "kill" );
	m_name_end.push_back( "gul" );
	m_name_end.push_back( "gok" );
	m_name_end.push_back( "tan" );
	m_name_end.push_back( "tok" );
	m_name_end.push_back( "bul" );
	m_name_end.push_back( "zod" );
	m_name_end.push_back( "zed" );
	m_name_end.push_back( "dor" );
	m_name_end.push_back( "grim" );
	m_name_end.push_back( "yohn" );
	m_name_end.push_back( "fan" );

	Spawn();
}


MobFactory::~MobFactory()
{
	for (mob_v::iterator it = m_mobs.begin(); it != m_mobs.end(); it++)
	{
		MOB *p = *it;
		delete p;
	}
}


void MobFactory::Spawn()
{
	int x;
	int y;
	std::string loc;
	std::string name;

	m_handler.GetWorld().GetRandomLocation(x,y,loc);

	name = m_name_beg[random() % m_name_beg.size()] +
	       m_name_end[random() % m_name_end.size()];
	name[0] = name[0] - 32;
	{
		std::string str;
		str = name + " enters the world\n";
		static_cast<SmallHandler&>(Handler()).Event(x,y,str);
	}
	MOB *p = new MOB(m_handler,x,y,name);
	m_mobs.push_back(p);
}


void MobFactory::RandomAction()
{
	MOB *p = m_mobs[random() % m_mobs.size()];
	switch(random() % 10)
	{
	case 0:
		p -> Create();
		break;
	default:
		p -> Move();
		break;
	}
}


void MobFactory::MOB::Move()
{
	int ny_x = m_x;
	int ny_y = m_y;
	std::string dir;
	std::string rdir;
	std::string str;
	bool n,s,e,w;
	bool open = false;
	m_handler.GetWorld().GetAt(m_x,m_y,str,n,s,e,w);
	switch(random() % 4)
	{
	case 0: // n
		ny_y--;
		dir = "north";
		rdir = "south";
		open = n;
		break;
	case 1: // s
		ny_y++;
		dir = "south";
		rdir = "north";
		open = s;
		break;
	case 2: // e
		ny_x++;
		dir = "east";
		rdir = "west";
		open = e;
		break;
	case 3: // w
		ny_x--;
		dir = "west";
		rdir = "east";
		open = w;
		break;
	}
	if (open && m_handler.GetWorld().FindAt(ny_x,ny_y,str))
	{
		static_cast<SmallHandler&>(m_handler.GetWorld().Handler()).Event(m_x,m_y,m_name + " leaves " + dir + "\n");
		SetNewPos(ny_x,ny_y);
		static_cast<SmallHandler&>(m_handler.GetWorld().Handler()).Event(m_x,m_y,m_name + " enters from the " + rdir + "\n");
	}
}


void MobFactory::MOB::Create()
{
	int ny_x = m_x;
	int ny_y = m_y;
	std::string dir;
	std::string rdir;
	switch(random() % 4)
	{
	case 0: // n
		ny_y--;
		dir = "north";
		rdir = "south";
		break;
	case 1: // s
		ny_y++;
		dir = "south";
		rdir = "north";
		break;
	case 2: // e
		ny_x++;
		dir = "east";
		rdir = "west";
		break;
	case 3: // w
		ny_x--;
		dir = "west";
		rdir = "east";
		break;
	}
	std::string str;
	if (!m_handler.GetWorld().FindAt(ny_x,ny_y,str))
	{
		str = "A small cell (created by " + m_name + ")";
		m_handler.GetWorld().AddAt(ny_x,ny_y,str);
		m_handler.GetWorld().Open(m_x,m_y,dir);
		m_handler.GetWorld().Open(ny_x,ny_y,rdir);
		static_cast<SmallHandler&>(m_handler.GetWorld().Handler()).Event(m_x,m_y,m_name + " creates a cell to the " + dir + "\n");
		static_cast<SmallHandler&>(m_handler.GetWorld().Handler()).Event(m_x,m_y,m_name + " leaves " + dir + "\n");
		SetNewPos(ny_x,ny_y);
	}
}


void MobFactory::MOB::SetNewPos(int x,int y)
{
	m_x = x;
	m_y = y;
}


void MobFactory::ShowNamesAt(SmallSocket *p,int x,int y,const std::string& prefix)
{
	for (mob_v::iterator it = m_mobs.begin(); it != m_mobs.end(); it++)
	{
		MOB *m = *it;
		if (m -> m_x == x && m -> m_y == y)
		{
			p -> Send("  " + prefix + m -> m_name + "\n");
		}
	}
}


