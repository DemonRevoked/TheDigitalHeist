\
/*
 * Berlin's Locker Controller (intentionally vulnerable)
 *
 * Purpose: rotate/backup locker logs. Installed SUID root.
 *
 * Vulnerability: calls "backup" via execvp() without absolute path,
 * inheriting user-controlled PATH.
 *
 * This is a controlled CTF target. Do not deploy on production systems.
 */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

static void usage(const char *p) {
  fprintf(stderr,
    "Berlin's Locker Controller\n"
    "Usage:\n"
    "  %s rotate <logfile>\n\n"
    "Example:\n"
    "  %s rotate /opt/lockers/logs/heist.log\n", p, p);
}

int main(int argc, char **argv) {
  if (argc != 3) { usage(argv[0]); return 1; }
  if (strcmp(argv[1], "rotate") != 0) { usage(argv[0]); return 1; }

  const char *logfile = argv[2];

  // Cosmetic check (not a security control)
  if (strncmp(logfile, "/opt/lockers/logs/", 17) != 0) {
    fprintf(stderr, "LockerCtl: only logs under /opt/lockers/logs/ are supported.\n");
    return 2;
  }

  // Intentionally uses execvp with non-absolute program name:
  // PATH will be consulted to locate "backup".
  char *const args[] = { "backup", (char*)logfile, NULL };

  execvp("backup", args);

  perror("execvp");
  return 3;
}
