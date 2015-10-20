/*
 * audio.h
 * 
 * Copyright 2014 marcell <marcell@nano>
 * 
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
 * MA 02110-1301, USA.
 */
#ifndef __AUDIO_H__
#define __AUDIO_H__

#include <jack/jack.h>

jack_port_t *input_portL;
jack_port_t *input_portR;
jack_port_t *output_portL;
jack_port_t *output_portR;
jack_client_t *client;
jack_default_audio_sample_t *OUTL;
jack_default_audio_sample_t *OUTR;
int nframez;
int process (jack_nframes_t nframes, void *arg);
void jack_shutdown (void *arg);
int mainz();

#endif //__AUDIO_H__
