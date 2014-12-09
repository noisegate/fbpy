/** @file simple_client.c
 *
 * @brief This simple client demonstrates the most basic features of JACK
 * as they would be used by many applications.
 * 
 * Marcell:
 * Downloaded it from http://trac.jackaudio.org/browser/trunk/jack/example-clients/simple_client.c
 */

#include <stdio.h>
#include <errno.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include "audio.h"

/**
 * The process callback for this JACK application is called in a
 * special realtime thread once for each audio cycle.
 *
 * This client does nothing more than copy data from its input
 * port to its output port. It will exit when stopped by 
 * the user (e.g. using Ctrl-C on a unix-ish operating system)
 */
int process (jack_nframes_t nframes, void *arg)
{
    static int i=0;

	jack_default_audio_sample_t *in, *out;
	
    i++;
    
	in = jack_port_get_buffer (input_portL, nframes);
	OUTL = jack_port_get_buffer (output_portL, nframes);
	memcpy (OUTL, in,
		sizeof (jack_default_audio_sample_t) * nframes);
    in = jack_port_get_buffer (input_portR, nframes);
    OUTR = jack_port_get_buffer (output_portR, nframes);
	memcpy (OUTR, in,
		sizeof (jack_default_audio_sample_t) * nframes);
    if (i>100){
        i=0;
        //printf("sample %i, value = %f\n", i, *(OUT+0));
    }
    nframez = (int)nframes;
	return 0;      
}

/**
 * JACK calls this shutdown_callback if the server ever shuts down or
 * decides to disconnect the client.
 */
void jack_shutdown (void *arg)
{
	exit (1);
}

void kwit()
{
    jack_client_close (client);
}

int getnframes()
{
    //only correct after process has been called
    return nframez;
}

int readout(double *dataL, double *dataR)
{
    int i;
    for (i=0;i<nframez;i++){
        //printf("val %f :",*(OUT+i));
        *(dataL+i) = (double)*(OUTL+i);
        *(dataR+i) = (double)*(OUTR+i);
    }
}

int mainz ()
{
	const char **ports;
	const char *client_name = "fbpy";
	const char *server_name = NULL;
	jack_options_t options = JackNullOption;
	jack_status_t status;
    
    static char visits = 0;
	
	/* open a client connection to the JACK server */

    if (visits>1){
        fprintf(stdout, "Only one instance supported, yet\n");
        return -1;
    }

	client = jack_client_open (client_name, options, &status, server_name);
	if (client == NULL) {
		fprintf (stderr, "jack_client_open() failed, "
			 "status = 0x%2.0x\n", status);
		if (status & JackServerFailed) {
			fprintf (stderr, "Unable to connect to JACK server\n");
		}
		exit (1);
	}
	if (status & JackServerStarted) {
		fprintf (stderr, "JACK server started\n");
	}
	if (status & JackNameNotUnique) {
		client_name = jack_get_client_name(client);
		fprintf (stderr, "unique name `%s' assigned\n", client_name);
	}

	/* tell the JACK server to call `process()' whenever
	   there is work to be done.
	*/

	jack_set_process_callback (client, process, 0);

	/* tell the JACK server to call `jack_shutdown()' if
	   it ever shuts down, either entirely, or if it
	   just decides to stop calling us.
	*/

	jack_on_shutdown (client, jack_shutdown, 0);

	/* display the current sample rate. 
	 */

	printf ("engine sample rate: %" PRIu32 "\n",
		jack_get_sample_rate (client));

	/* create two ports */

	input_portL = jack_port_register (client, "input0",
					 JACK_DEFAULT_AUDIO_TYPE,
					 JackPortIsInput, 0);
	input_portR = jack_port_register (client, "input1",
					 JACK_DEFAULT_AUDIO_TYPE,
					 JackPortIsInput, 0);                     
	output_portL = jack_port_register (client, "output0",
					  JACK_DEFAULT_AUDIO_TYPE,
					  JackPortIsOutput, 0);
	output_portR = jack_port_register (client, "output1",
					  JACK_DEFAULT_AUDIO_TYPE,
					  JackPortIsOutput, 0);

	if ((input_portL == NULL) || (output_portL == NULL)) {
		fprintf(stderr, "no more JACK ports available\n");
		exit (1);
	}

	if ((input_portR == NULL) || (output_portR == NULL)) {
		fprintf(stderr, "no more JACK ports available\n");
		exit (1);
	}

	/* Tell the JACK server that we are ready to roll.  Our
	 * process() callback will start running now. */

	if (jack_activate (client)) {
		fprintf (stderr, "cannot activate client");
		exit (1);
	}

	/* Connect the ports.  You can't do this before the client is
	 * activated, because we can't make connections to clients
	 * that aren't running.  Note the confusing (but necessary)
	 * orientation of the driver backend ports: playback ports are
	 * "input" to the backend, and capture ports are "output" from
	 * it.
	 */

	ports = jack_get_ports (client, NULL, NULL,
				JackPortIsPhysical|JackPortIsOutput);
	if (ports == NULL) {
		fprintf(stderr, "no physical capture ports\n");
		exit (1);
	}

	//if (jack_connect (client, ports[0], jack_port_name (input_port))) {
	//	fprintf (stderr, "cannot connect input ports\n");
	//}

	free (ports);
	
	ports = jack_get_ports (client, NULL, NULL,
				JackPortIsPhysical|JackPortIsInput);
	if (ports == NULL) {
		fprintf(stderr, "no physical playback ports\n");
		exit (1);
	}

	//if (jack_connect (client, jack_port_name (output_port), ports[0])) {
	//	fprintf (stderr, "cannot connect output ports\n");
	//}

	free (ports);

	/* keep running until stopped by the user */

	/*sleep (-1);

	/* this is never reached but if the program
	   had some other way to exit besides being killed,
	   they would be important to call.
	*/

	//jack_client_close (client);
	//exit (0);
    
    return 0;
}
