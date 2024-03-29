import sys

# Ensure default sub-command is always "list-important-focus-targets"
if len(sys.argv) < 2:
    sys.argv.append('l')

from datetime import datetime
import click
import utils
import dao
import os


class AliasedGroup(click.Group):

    SUBCOMMAND_SHORTCUTS = {
        'a': 'add-focus-target',
        'add': 'add-focus-target',
        'r': 'rename-focus-target',
        'rename': 'rename-focus-target',
        'd': 'defer-focus-target',
        'defer': 'defer-focus-target',
        'h': 'hasten-focus-target',
        'hasten': 'hasten-focus-target',
        'k': 'kill-focus-target',
        'kill': 'kill-focus-target',
        'e': 'edit-focus-target-description',
        'ed': 'edit-focus-target-description',
        'edit': 'edit-focus-target-description',
        'i': 'set-focus-target-importance',
        'si': 'set-focus-target-importance',
        'set-importance': 'set-focus-target-importance',
        'l': 'list-important-focus-targets',
        'li': 'list-important-focus-targets',
        'list': 'list-important-focus-targets',
        'list-important': 'list-important-focus-targets',
        'la': 'list-all-focus-targets',
        'list-all': 'list-all-focus-targets',
        'ss': 'set-focus-span',
        'set-span': 'set-focus-span'
    }

    def get_command(self, ctx, cmd_name):
        return super().get_command(ctx, __class__.SUBCOMMAND_SHORTCUTS.get(cmd_name, cmd_name))
    
    def resolve_command(self, ctx, args):
        _, cmd, args = super().resolve_command(ctx, args)
        return cmd.name, cmd, args

@click.command(cls=AliasedGroup)
def mem():
    dao.init_memstate_if_not_exist()
    dao.init_memfiles_if_not_exist()

@mem.command()
@click.argument("name", nargs=1, type=click.STRING)
@click.argument("importance", nargs=1, type=click.INT)
@click.argument("description", nargs=1, type=click.STRING, default="")
def add_focus_target(*args, **kwargs):
    memstate = dao.load_memstate()
    name = kwargs["name"]
    description = kwargs["description"]
    focus_targets = memstate["focus_targets"]
    importance = kwargs["importance"]

    if name in focus_targets:
        raise click.ClickException(f'Focus target "{name}" already exists!  Operation aborted.')

    if importance < 1 or importance > 5:
        raise click.ClickException(f'Focus importance must range from 1 to 5 (inclusive)!  Operation aborted.')

    nowstr = datetime.isoformat(datetime.utcnow())
    focus_targets[name] = {"importance": kwargs["importance"], "created": nowstr}

    dao.save_memstate(memstate)
    dao.save_description(name, description)

@mem.command()
@click.argument("old_name", nargs=1, type=click.STRING)
@click.argument("new_name", nargs=1, type=click.STRING)
def rename_focus_target(*args, **kwargs):
    memstate = dao.load_memstate()
    old_name = kwargs["old_name"]
    new_name = kwargs["new_name"]

    focus_targets = memstate["focus_targets"]

    if old_name not in focus_targets:
        raise click.ClickException(f'Focus target "{old_name}" doesn\'t exist!  Operation aborted.')
    if new_name in focus_targets:
        raise click.ClickException(f'Focus target "{new_name}" already exists!  Operation aborted.')

    focus_targets[new_name] = focus_targets[old_name]
    del focus_targets[old_name]

    dao.save_memstate(memstate)
    dao.rename_description(old_name, new_name)

@mem.command()
@click.argument("name", nargs=1, type=click.STRING)
@click.argument("delay", nargs=1, type=click.STRING)
def defer_focus_target(*args, **kwargs):
    memstate = dao.load_memstate()

    name = kwargs["name"]
    delay = kwargs["delay"]
    focus_targets = memstate["focus_targets"]

    if name not in focus_targets:
        raise click.ClickException(f'Focus target "{name}" doesn\'t exists!  Operation aborted.')

    deferred_to = utils.parse_delay(delay).isoformat()  # UTC

    focus_targets[name]["deferred_to"] = deferred_to

    dao.save_memstate(memstate)

@mem.command()
@click.argument("name", nargs=1, type=click.STRING)
def hasten_focus_target(*args, **kwargs):
    memstate = dao.load_memstate()

    name = kwargs["name"]
    focus_targets = memstate["focus_targets"]

    if name not in focus_targets:
        raise click.ClickException(f'Focus target "{name}" doesn\'t exists!  Operation aborted.')

    focus_target = focus_targets[name]
    del focus_target["deferred_to"]

    dao.save_memstate(memstate)

@mem.command()
@click.argument("name", nargs=1, type=click.STRING)
def kill_focus_target(*args, **kwargs):
    memstate = dao.load_memstate()
    focus_targets = memstate["focus_targets"]
    name = kwargs["name"]

    if name not in focus_targets:
        raise click.ClickException(f'Focus target "{name}" doesn\'t exist!  Operation aborted.')

    del focus_targets[name]
    dao.save_memstate(memstate)

    dao.delete_description(name)

@mem.command()
@click.argument("name", nargs=1, type=click.STRING)
def edit_focus_target_description(*args, **kwargs):
    name = kwargs["name"]

    memstate = dao.load_memstate()
    focus_targets = memstate["focus_targets"]

    if name not in focus_targets:
        raise click.ClickException(f'Focus target "{name}" doesn\'t exist!  Operation aborted.')

    cmd = utils.get_config()["DESCRIPTION_EDITOR_OPEN_COMMAND"]
    fname = dao.get_description_filename(name)

    os.system(f"{cmd} \"{fname}\"")

@mem.command()
@click.argument("name", nargs=1, type=click.STRING)
@click.argument("importance", nargs=1, type=click.INT)
def set_focus_target_importance(*args, **kwargs):
    name = kwargs["name"]
    importance = kwargs["importance"]

    if importance < 1 or importance > 5:
        raise click.ClickException(f'Focus importance must range from 1 to 5 (inclusive)!  Operation aborted.')

    memstate = dao.load_memstate()
    targets = memstate["focus_targets"]

    if name not in targets:
        raise click.ClickException(f'Focus target "{name}" doesn\'t exist!  Operation aborted.')

    targets[name]["importance"] = importance

    dao.save_memstate(memstate)

@mem.command()
def list_important_focus_targets(*args, **kwargs):
    memstate = dao.load_memstate()
    focus_span = memstate["focus_span"]
    targets = memstate["focus_targets"]
    targets = list(targets.items())

    now = datetime.utcnow()
    def is_deferred(target):
        deferred_to = target[1].get("deferred_to")  # UTC
        if not deferred_to:
            return False
        return now <= datetime.fromisoformat(deferred_to)

    targets.sort(key=lambda target: target[1]["importance"], reverse=True)
    curr_targets, defer_targets = [], []
    for target in targets:
        if not is_deferred(target):
            curr_targets.append(target)
        else:
            defer_targets.append(target)
    targets = curr_targets + defer_targets

    for idx, target in enumerate(targets):
        if idx >= focus_span:
            break
        importance = target[1]["importance"]
        name = target[0]
        snippet = dao.load_description_snippet(name)
        if not snippet:
            snippet = "(empty)"
        if is_deferred(target):
            deferred_to = datetime.fromisoformat(target[1]["deferred_to"])
            deferred_to = utils.convert_utc_to_local(deferred_to)
            deferred_weekday = deferred_to.strftime("%A")[:3]
            deferred_to = deferred_to.strftime("%m/%d")
            name = f"[{deferred_weekday} {deferred_to}] {name}"
        print(importance, ":", name, "-", snippet)
    print(f"\n==> {len(defer_targets)} Deferred Items; {len(targets)} Total Items")

@mem.command()
def list_all_focus_targets(*args, **kwargs):
    targets = dao.load_memstate()["focus_targets"]
    targets = list(targets.items())

    now = datetime.utcnow()
    def is_deferred(target):
        deferred_to = target[1].get("deferred_to")  # UTC
        if not deferred_to:
            return False
        return now <= datetime.fromisoformat(deferred_to)

    targets.sort(key=lambda target: int(target[1]["importance"]), reverse=True)
    curr_targets, defer_targets = [], []
    for target in targets:
        if not is_deferred(target):
            curr_targets.append(target)
        else:
            defer_targets.append(target)
    targets = curr_targets + defer_targets

    for target in targets:
        importance = target[1]["importance"]
        name = target[0]
        snippet = dao.load_description_snippet(name)
        if not snippet:
            snippet = "(empty)"
        if is_deferred(target):
            deferred_to = datetime.fromisoformat(target[1]["deferred_to"])
            deferred_to = utils.convert_utc_to_local(deferred_to)
            deferred_weekday = deferred_to.strftime("%A")[:3]
            deferred_to = deferred_to.strftime("%m/%d")
            name = f"[{deferred_weekday} {deferred_to}] {name}"
        print(importance, ":", name, "-", snippet)
    print(f"\n==> {len(defer_targets)} Deferred Items; {len(targets)} Total Items")

@mem.command()
@click.argument("span", nargs=1, type=click.INT)
def set_focus_span(*args, **kwargs):
    span = kwargs["span"]
    if span < 1:
        raise click.ClickException(f"Focus span must be 1 or greater!  Operation aborted.")
    memstate = dao.load_memstate()
    memstate["focus_span"] = span
    dao.save_memstate(memstate)

if __name__ == '__main__':
    mem()