import logging
from telegrambot import main, TelegramBot
from telegrambot.commands import RedditCommand, GetCommand
from hotslogs import get_hots_tier_list

logger = logging.getLogger('gearbot')


class EyebleachCommand(RedditCommand):
    subreddits = ['stacked', 'tightdresses', 'boobs', 'bustypetite', 'hotness']
    command_reddit = None
    command_eyebleach = RedditCommand._cmd_reddit
    command_eyecandy = RedditCommand._cmd_reddit


class HotsCommand(object):
    def command_hots(self, *args, bot=None, update=None):
        """
        /hots tier
          
          Gets the latest tier list compiled from hotslogs.com data.
        """
        if not (args and bot and update):
            return
        
        logger.info('"/{command}" from {user}'.format(
            command=' '.join([update.command] + update.command_args),
            user=update.message.user.username,
        ))

        def hots_tier_list(*subargs):
            if subargs:
                wanted_tier = ' '.join(subargs)
                try:
                    wanted_tier = int(wanted_tier)
                except ValueError:
                    return self.send_message(update.message.chat.id,
                                      'There is no "{}" tier. Try '
                                      'using numbers, fool.'.format(
                                          wanted_tier))
            else:
                wanted_tier = None
            tiers = get_hots_tier_list(self)
            filled_tiers = [k for k, v in tiers.items() if k and v]
            if wanted_tier and wanted_tier not in filled_tiers:
                return self.send_message(update.message.chat.id,
                                  'There are only {max} tiers right now, '
                                  'not {wanted}.'.format(
                                      max=max(filled_tiers),
                                      wanted=wanted_tier,
                                  ))

            message = ['HotS Tier List (Ranked)',
                       '']
            for tier, heroes in tiers.items():
                if not heroes:
                    continue
                if wanted_tier and wanted_tier != tier:
                    continue
                if tier is not None:
                    message.append('** Tier {} **'.format(tier).upper())
                else:
                    message.append('** Untiered **'.upper())
                for hero in heroes:
                    message.append(' - {name} \t({win_pct}%)'.format(
                        name=hero.get('hero'),
                        win_pct=hero.get('win-percent'),
                    ))
            return self.send_message(update.message.chat.id, 
                                     '\n'.join(message))
        
        def hots_hero_tier(*subargs):
            if not subargs:
                return
            hero_name = ' '.join(subargs)
            tiers = get_hots_tier_list(self)

            def compare_hero_names(one, two):
                # normalize the names as much as possible
                names = []
                for name in [one, two]:
                    names.append(name.strip().replace('\'', '').lower())
                return len(set(names)) == 1

            hero = None
            tier = None
            for _tier, heroes in tiers.items():
                for _hero in heroes:
                    if not compare_hero_names(_hero.get('hero'), hero_name):
                        continue
                    hero = _hero
                    break
                if hero:
                    tier = _tier
                    break
            if not hero:
                return self.send_message(update.message.chat.id,
                                         'Hero "{name}" not found. Hero is '
                                         'either not rated yet, or you '
                                         'misspelled the name.'.format(
                                             name=hero_name,
                                         ))
            message = [
                '- {name}\n'
                'Tier: {tier}\n'
                'Win Rate: {pct}%\n'
                'Popularity: {pop}%'.format(
                    name=hero.get('hero'),
                    tier=tier,
                    pct=hero.get('win-percent'),
                    pop=hero.get('popularity'),
                )
            ]
            return self.send_message(update.message.chat.id, 
                                     '\n'.join(message))
        
        try:
            subcommand, subargs = args[0], args[1:]
        except IndexError:
            subcommand, subargs = args[0], None
        
        self.send_chat_action(update.message.chat.id)
        if subcommand == 'tier':
            return hots_tier_list(*subargs)
        if subcommand == 'hero':
            return hots_hero_tier(*subargs)


class TelegramBot(TelegramBot, GetCommand, EyebleachCommand, HotsCommand):
    pass


if __name__ == '__main__':
    main(bot_class=TelegramBot)
