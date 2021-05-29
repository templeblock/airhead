from os.path import join

import numpy as np

import utils.helper as hlp
from utils.helper import log

if __name__ == '__main__':
    hlp.hi('Analysis')

    model_name = 'unet_baseline'

    for version in (3,5,6):
        #version = 6

        log(f'version {version}',color='cyan')

        result_dir = join(hlp.LOG_DIR, 'results', model_name)

        results = np.load(join(result_dir, f'{model_name}_v{version}.npy'), allow_pickle=True)

        dice = []
        dice_et = []
        dice_tc = []
        dice_wt = []
        hd = []
        hd_et = []
        hd_tc = []
        hd_wt = []

        best = 0
        id = None

        for res in results:

            if res['test_dice_metric'] > best:
                id = res['id']

            dice.append(res['test_dice_metric'])
            dice_et.append(res['test_dice_et'])
            dice_tc.append(res['test_dice_tc'])
            dice_wt.append(res['test_dice_wt'])
            hd.append(res['test_hd_metric'])
            hd_et.append(res['test_hd_et'])
            hd_tc.append(res['test_hd_tc'])
            hd_wt.append(res['test_hd_wt'])

        print('dice: ', np.mean(dice))
        print('dice et: ', np.mean(dice_et))
        print('dice tc: ', np.mean(dice_tc))
        print('dice wt: ', np.mean(dice_wt))

        print('hd: ', np.mean(hd))
        print('hd et: ', np.mean(hd_et))
        print('hd tc: ', np.mean(hd_tc))
        print('hd wt: ', np.mean(hd_wt))
