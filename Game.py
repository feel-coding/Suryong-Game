import random, sys, time, math, pygame
import numpy as np
from pygame.locals import *

FPS = 30  # 화면을 얼마나 업데이트할지 FPS
WINWIDTH = 640  # 프로그램 윈도우 너비. 픽셀 단위
WINHEIGHT = 480  # 윈도우의 높이. 픽셀 단위
HALF_WINWIDTH = int(WINWIDTH / 2)
HALF_WINHEIGHT = int(WINHEIGHT / 2)

GRASSCOLOR = (24, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
Light_Purple = (228, 203, 255)

CAMERASLACK = 90  # 중앙에서 수룡이가 얼마나 멀어지면 카메라를 움직일지 결정
MOVERATE = 9  # 수룡이의 이동속도
BOUNCERATE = 6  # 수룡이의 점프속도(숫자가 클수록 느려짐)
BOUNCEHEIGHT = 30  # 점프 높이
STARTSIZE = 50  # 게임 시작할 때 수룡이 사이즈
WINSIZE = 200  # 이기려면 수룡이가 얼마나 커져야 하는지
INVULNTIME = 2  # 스펙틀과 부딪힌 다음 얼마동안 무적인지(초 단위)
GAMEOVERTIME = 4  # Game Over를 화면에 몇 초간 보여줄지
MAXHEALTH = 3  # 수룡이의 시작 목숨 수

NUMGRASS = 80  # 활성 영역 안에 진디 객체 수
NUMSPECS = 35  # 활성 영역 안에 스펙 수
MINSPEED = 3  # 가장 느린 스펙 객체 스피드
MAXSPEED = 7  # 가장 빠른 스펙 객체 스피드
DIRCHANGEFREQ = 2  # 프레임당 방향을 바꿀 수 있는 확률. % 단위

ROUND = 1


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, SOO, GRASSIMAGES, FGRADE, AGRADE, JOB, CERTIFICATION, SPECIMAGES, POSITIVES, GRADUATION, AWARD, SUJUNGBALL, MEDIUMFONT, SMALLFONT, ROUND, HIGHESTROUND, HIGHESTSCORE

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_icon(pygame.image.load('gameicon.png'))
    DISPLAYSURF = pygame.display.set_mode((WINWIDTH, WINHEIGHT))
    pygame.display.set_caption('수룡이의 스펙 쌓기')

    # 파이게임 글씨 폰트
    BASICFONT = pygame.font.Font('freesansbold.ttf', 32)
    MEDIUMFONT = pygame.font.Font('freesansbold.ttf', 20)
    SMALLFONT = pygame.font.Font('freesansbold.ttf', 17)

    # 이미지 파일 로드

    SOO = pygame.image.load('suryong.png')  # 수룡이 이미지
    AGRADE = pygame.image.load('agrade.png')
    FGRADE = pygame.image.load('fgrade.png')
    AWARD = pygame.image.load('award.png')
    SUJUNGBALL = pygame.image.load('sujungball.png')
    GRADUATION = pygame.image.load('graduation.png')
    JOB = pygame.image.load('job.png')
    CERTIFICATION = pygame.image.load('certification.png')
    GRASSIMAGES = []
    for i in range(1, 5):
        GRASSIMAGES.append(pygame.image.load('grass%s.png' % i))
    SPECIMAGES = [AGRADE, FGRADE, SUJUNGBALL, AWARD, CERTIFICATION, JOB, GRADUATION]
    POSITIVES = [0, 2, 3, 4, 5, 6]  # A 학점, 인턴, 프로젝트 경험 등 긍정적인 스펙들의 인덱스

    while True:
        runGame()


def runGame():
    # 새 게임 시작시 변수 설정
    invulnerableMode = False  # 수룡이가 스펙을 먹고 무적이 되었는지, 무적: 충돌 무시
    invulnerableStartTime = 0  # 무적이 되기 시작한 시간
    gameOverMode = False  # 수룡이 죽었을 때
    gameOverStartTime = 0  # 수룡이가 죽은 시간
    winMode = False  # 이겼을 때

    global ROUND
    global NUMSPECS

    # 게임의 필요한 글씨를 쓰기 위한 surface를 만든다.
    gameOverSurf = BASICFONT.render('Game is Over', True, BLACK)
    gameOverRect = gameOverSurf.get_rect()
    gameOverRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)

    winSurf = BASICFONT.render('Congratulations! You Win', True, BLACK)
    winRect = winSurf.get_rect()
    winRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)

    winSurf2 = BASICFONT.render('Press R to next level', True, BLACK)
    winRect2 = winSurf2.get_rect()
    winRect2.center = (HALF_WINWIDTH, HALF_WINHEIGHT + 50)

    startSurf = BASICFONT.render('Press S to try again', True, BLACK)
    startRect = winSurf.get_rect()
    startRect.center = (HALF_WINWIDTH + 50, HALF_WINHEIGHT + 50)

    # 카메라뷰 가장 왼쪽 상단 좌표
    camerax = 0
    cameray = 0

    grassObjs = []  # 게임의 모든 잔디 객체 저장
    specObjs = []  # 스펙 객체들 저장

    # player 수룡이 객체. 클래스를 만들지 않고 딕셔너리로 수룡이 객체를 표현함
    suryongObj = {
        'surface': pygame.transform.scale(SOO, (STARTSIZE, STARTSIZE)),#수룡이 이미지를 담고 있음
                  'size': STARTSIZE, #수룡이의 크기
                  'x': HALF_WINWIDTH,
                  'y': HALF_WINHEIGHT,
                  'bounce': 0, #0이면 점프 안 하고 그냥 서있는거
                  'health': MAXHEALTH,  # 목숨이 몇 개 남았는지
                  'countSujungBalls': 0,# 수정구 몇 개 먹었는지
                  'score': 0}
    try:
        file = open("highest.txt", mode='r')
        file.close()
    except FileNotFoundError:
        file = open("highest.txt", mode='w')
        file.write("1 0")
        file.close()
    file = open("highest.txt", mode='r')
    s = file.readline()
    highestRound, highestScore = s.split()

    moveLeft = False
    moveRight = False
    moveUp = False
    moveDown = False

    # 화면 상에 무작위로 잔디를 늘어놓고 시작
    for i in range(10):
        grassObjs.append(makeNewGrass(camerax, cameray))
        grassObjs[i]['x'] = random.randint(0, WINWIDTH)
        grassObjs[i]['y'] = random.randint(0, WINHEIGHT)

    while True:  # 메인 게임 루프
        # 무적 상태를 꺼야하는지 검사
        if invulnerableMode and time.time() - invulnerableStartTime > INVULNTIME: #2초가 지나면 무적상태 해제
            invulnerableMode = False

        # 스펙들이 움직이며 돌아다님
        for sObj in specObjs:
            # 스펙들을 움직이면서 점프하는 것을 조정
            sObj['x'] += sObj['movex']
            sObj['y'] += sObj['movey']
            sObj['bounce'] += 1
            if sObj['bounce'] > sObj['bouncerate']:
                sObj['bounce'] = 0  # 점프하는 정도 리셋

            # 무작위로 방향을 바꾼다
            if random.randint(0, 99) < DIRCHANGEFREQ:
                sObj['movex'] = getRandomVelocity()
                sObj['movey'] = getRandomVelocity()
                sObj['surface'] = pygame.transform.scale(sObj['surface'], (sObj['width'], sObj['height']))

        # 객체를 모두 살펴본 후 지워야할 것이 있는지 검사
        for i in range(len(grassObjs) - 1, -1, -1):
            if isOutsideActiveArea(camerax, cameray, grassObjs[i]):
                del grassObjs[i]
        for i in range(len(specObjs) - 1, -1, -1):
            if isOutsideActiveArea(camerax, cameray, specObjs[i]):
                del specObjs[i]

        # 잔디와 스펙들이 중분하지 않으면 추가
        while len(grassObjs) < NUMGRASS:
            grassObjs.append(makeNewGrass(camerax, cameray))
        if ROUND == 1:
            while len(specObjs) < NUMSPECS:
                specObjs.append(firstRoundMakeNewSpec(camerax, cameray))
        elif ROUND == 2:
            while len(specObjs) < NUMSPECS:
                specObjs.append(secondRoundMakeNewSpec(camerax, cameray))
        elif ROUND >= 3:
            while len(specObjs) < NUMSPECS:
                specObjs.append(thirdRoundMakeNewSpec(camerax, cameray))

        # 카메라 슬랙을 벗어났으면 카메라 좌표 조정
        playerCenterx = suryongObj['x'] + int(suryongObj['size'] / 2)
        playerCentery = suryongObj['y'] + int(suryongObj['size'] / 2)
        if (camerax + HALF_WINWIDTH) - playerCenterx > CAMERASLACK:
            camerax = playerCenterx + CAMERASLACK - HALF_WINWIDTH
        elif playerCenterx - (camerax + HALF_WINWIDTH) > CAMERASLACK:
            camerax = playerCenterx - CAMERASLACK - HALF_WINWIDTH

        if (cameray + HALF_WINHEIGHT) - playerCentery > CAMERASLACK:
            cameray = playerCentery + CAMERASLACK - HALF_WINHEIGHT
        elif playerCentery - (cameray + HALF_WINHEIGHT) > CAMERASLACK:
            cameray = playerCentery - CAMERASLACK - HALF_WINHEIGHT

        # 배경화면 그리기
        DISPLAYSURF.fill(Light_Purple)

        # 화면에 모든 잔디 객체 그리기
        for gObj in grassObjs:
            gRect = pygame.Rect((gObj['x'] - camerax,
                                 gObj['y'] - cameray,
                                 gObj['width'],
                                 gObj['height']))
            DISPLAYSURF.blit(GRASSIMAGES[gObj['grassImage']], gRect)

        # 스펙들을 화면에 그리기
        for sObj in specObjs:
            sObj['rect'] = pygame.Rect((sObj['x'] - camerax,
                                        sObj['y'] - cameray - getBounceAmount(sObj['bounce'], sObj['bouncerate'],
                                                                              sObj['bounceheight']),
                                        sObj['width'],
                                        sObj['height']))
            DISPLAYSURF.blit(sObj['surface'], sObj['rect'])

        # player 수룡이 그리기
        flashIsOn = round(time.time(), 1) * 10 % 2 == 1
        if not gameOverMode and not (invulnerableMode and flashIsOn):
            suryongObj['rect'] = pygame.Rect((suryongObj['x'] - camerax,
                                              suryongObj['y'] - cameray - getBounceAmount(suryongObj['bounce'],
                                                                                          BOUNCERATE, BOUNCEHEIGHT),
                                              suryongObj['size'],
                                              suryongObj['size']))
            DISPLAYSURF.blit(suryongObj['surface'], suryongObj['rect'])

        # 갖고 있는 목숨 그리기
        drawHealthMeter(suryongObj['health'])

        drawScore(suryongObj['score'])
        drawSujungBallScore(suryongObj['countSujungBalls'])
        drawRound()
        drawHighestScore(highestRound, highestScore)

        for event in pygame.event.get():  # 이벤트 처리 루프
            if event.type == QUIT:
                terminate()

            elif event.type == KEYDOWN:
                if event.key in (K_UP, K_w):  # 윗쪽 방향키
                    moveDown = False
                    moveUp = True
                elif event.key in (K_DOWN, K_s):  # 아랫쪽 방향키
                    moveUp = False
                    moveDown = True
                elif event.key in (K_LEFT, K_a):  # 왼쪽 방향키
                    moveRight = False
                    moveLeft = True
                elif event.key in (K_RIGHT, K_d):  # 오른쪽 방향키
                    moveLeft = False
                    moveRight = True
                elif winMode and event.key == K_r:
                    ROUND += 1
                    NUMSPECS += 5
                    return


            elif event.type == KEYUP:
                # 수룡이를 멈춘다
                if event.key in (K_LEFT, K_a):
                    moveLeft = False
                elif event.key in (K_RIGHT, K_d):
                    moveRight = False
                elif event.key in (K_UP, K_w):
                    moveUp = False
                elif event.key in (K_DOWN, K_s):
                    moveDown = False

                elif event.key == K_ESCAPE:
                    terminate()

        if not gameOverMode:
            # 수룡이를 움직인다.
            if moveLeft:
                suryongObj['x'] -= MOVERATE
            if moveRight:
                suryongObj['x'] += MOVERATE
            if moveUp:
                suryongObj['y'] -= MOVERATE
            if moveDown:
                suryongObj['y'] += MOVERATE

            if (moveLeft or moveRight or moveUp or moveDown) or suryongObj['bounce'] != 0:
                suryongObj['bounce'] += 1

            if suryongObj['bounce'] > BOUNCERATE:
                suryongObj['bounce'] = 0  # 점프 정도 리셋

            # player 수룡이가 스펙과 부딪혔는지 아닌지 감지
            for i in range(len(specObjs) - 1, -1, -1):
                specObj = specObjs[i]
                if 'rect' in specObj and suryongObj['rect'].colliderect(specObj['rect']) and not winMode:
                    # 수룡이와 스펙의 충돌이 발생
                    if specObj['whatSpec'] in POSITIVES: #긍정적인 스펙을 먹었으면
                        suryongObj['size'] += int((specObj['width'] * specObj['height']) ** 0.2) + 1
                        suryongObj['score'] += 1
                        del specObjs[i]  # 수룡이와 닿으면 학점 객체 사라지도록
                        suryongObj['surface'] = pygame.transform.scale(SOO, (suryongObj['size'], suryongObj['size']))

                        if suryongObj['size'] > WINSIZE:
                            winMode = True  # 이겼으므로 winMode
                        if specObj['whatSpec'] == 2: #수정구를 먹었으면
                            suryongObj['countSujungBalls'] += 1  # 수정구 몇 개 먹었는지 세는 변수 1 증가
                        if suryongObj['countSujungBalls'] > 0 and suryongObj['countSujungBalls'] % 3 == 0 and suryongObj['health'] < 3:
                            suryongObj['health'] += 1
                            suryongObj['countSujungBalls'] = 0

                    elif not invulnerableMode:  # 부정적인 스펙을 먹었고 수룡이가 무적상태가 아니라면
                        invulnerableMode = True
                        invulnerableStartTime = time.time()
                        suryongObj['health'] -= 1  # 기회 하나 줄어듦.
                        suryongObj['countSujungBalls'] = 0

                        if suryongObj['health'] == 0:  # 3번의 목숨을 모두 쓰면
                            gameOverMode = True  # 이제 게임오버 모드
                            gameOverStartTime = time.time()
        else: # 게임이 끝났다면
            # "GAME OVER"라고 보여줌 + 시작 기능 추가
            DISPLAYSURF.blit(gameOverSurf, gameOverRect)
            DISPLAYSURF.blit(startSurf, startRect)
            if event.key == K_s:
                file = open("highest.txt", mode='r')
                s = file.readline()
                highestRound, highestScore = s.split()
                file.close()
                if ROUND > int(highestRound) or (
                        ROUND == int(highestRound) and suryongObj['score'] > int(highestScore)):
                    file = open("highest.txt", mode='w')
                    file.write("{} {}".format(ROUND, suryongObj['score']))
                    file.close()
                    breakRecordSurf = BASICFONT.render('YOU BROKE THE HIGHEST RECORD!!', True, WHITE)
                    DISPLAYSURF.blit(breakRecordSurf, breakRecordSurf.get_rect())
                return  # 게임을 끝냄. runGame 함수 끝내고 main 함수로 돌아감

        # 이겼으면
        if winMode:
            DISPLAYSURF.blit(winSurf, winRect)
            DISPLAYSURF.blit(winSurf2, winRect2)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def firstRoundMakeNewSpec(camerax, cameray):  # 학점이든 대외활동이든 스펙이든 랜덤으로 생성
    sp = {}
    indexList = [0, 1, 2]
    specIndex = np.random.choice(indexList, size=1, replace=True,
                                 p=[0.62, 0.3, 0.08])  # A, F, 수정구 중에서 랜덤으로 선택하되 수정구가 나올 확률은 8%
    sp['width'] = 55  # A, F의 크기
    sp['height'] = 55
    if specIndex == 2:
        sp['width'] = 30
        sp['height'] = 30

    sp['x'], sp['y'] = getRandomOffCameraPos(camerax, cameray, sp['width'], sp['height'])
    sp['movex'] = getRandomVelocity()
    sp['movey'] = getRandomVelocity()

    sp['surface'] = pygame.transform.scale(SPECIMAGES[specIndex[0]], (sp['width'], sp['height']))
    sp['bounce'] = 0
    sp['bouncerate'] = random.randint(10, 18)
    sp['bounceheight'] = random.randint(10, 50)
    sp['whatSpec'] = specIndex
    return sp


def secondRoundMakeNewSpec(camerax, cameray):  # 학점이든 대외활동이든 스펙이든 랜덤으로 생성
    sp = {}
    indexList = [0, 1, 2, 3, 4]
    specIndex = np.random.choice(indexList, size=1, replace=True,
                                 p=[0.17, 0.4, 0.08, 0.17, 0.18])  # A, F, 인턴, 공모전, 수정구 중에서 랜덤으로 선택하되 수정구가 나올 확률은 8%
    sp['width'] = 35
    sp['height'] = 35
    if specIndex in (0, 1):
        sp['width'] = 55
        sp['height'] = 55
    elif specIndex == 2:
        sp['width'] = 30
        sp['height'] = 30
    elif specIndex in (3, 4):
        sp['width'] = 55
        sp['height'] = 55

    sp['x'], sp['y'] = getRandomOffCameraPos(camerax, cameray, sp['width'], sp['height'])
    sp['movex'] = getRandomVelocity()
    sp['movey'] = getRandomVelocity()

    sp['surface'] = pygame.transform.scale(SPECIMAGES[specIndex[0]], (sp['width'], sp['height']))
    sp['bounce'] = 0
    sp['bouncerate'] = random.randint(10, 18)
    sp['bounceheight'] = random.randint(10, 50)
    sp['whatSpec'] = specIndex
    return sp


def thirdRoundMakeNewSpec(camerax, cameray):  # 스펙을 랜덤으로 생성
    sp = {}
    indexList = [0, 1, 2, 3, 4, 5, 6]
    specIndex = np.random.choice(indexList, size=1, replace=True,
                                 p=[0.094, 0.45, 0.08, 0.094, 0.094, 0.094, 0.094])
    # A, F, 인턴, 공모전, 수정구 중에서 랜덤으로 선택하되 수정구가 나올 확률은 8%
    sp['width'] = 70
    sp['height'] = 70
    if specIndex in (0, 1):
        sp['width'] = 55
        sp['height'] = 55
    elif specIndex == 2:
        sp['width'] = 30
        sp['height'] = 30
    elif specIndex in (3, 4):
        sp['width'] = 55
        sp['height'] = 55
    sp['x'], sp['y'] = getRandomOffCameraPos(camerax, cameray, sp['width'], sp['height'])
    sp['movex'] = getRandomVelocity()
    sp['movey'] = getRandomVelocity()

    sp['surface'] = pygame.transform.scale(SPECIMAGES[specIndex[0]], (sp['width'], sp['height']))
    sp['bounce'] = 0
    sp['bouncerate'] = random.randint(10, 18)
    sp['bounceheight'] = random.randint(10, 50)
    sp['whatSpec'] = specIndex
    return sp


def drawHealthMeter(currentHealth):  # 기회 몇 번 남았는지 표시해주는 왼쪽 위 그림
    for i in range(currentHealth):  # 빨간색 목숨 표시
        pygame.draw.rect(DISPLAYSURF, RED, (15, 5 + (10 * MAXHEALTH) - i * 10, 20, 10))
    for i in range(MAXHEALTH):  # 흰색 테두리
        pygame.draw.rect(DISPLAYSURF, WHITE, (15, 5 + (10 * MAXHEALTH) - i * 10, 20, 10), 1)


def drawScore(currentScore):  # 점수판
    score_text = BASICFONT.render('SCORE: {}'.format(currentScore), True, WHITE)
    score_textRect = score_text.get_rect()
    score_textRect.center = (550, 15)
    DISPLAYSURF.blit(score_text, score_textRect)


def drawSujungBallScore(numOfSujungBalls):  # 수정구 몇 개 먹었는지
    sujungBallScore = MEDIUMFONT.render('SUJUNG BALLS: {}'.format(numOfSujungBalls), True, WHITE)
    sujungBallScoreRect = sujungBallScore.get_rect()
    sujungBallScoreRect.center = (540, 50)
    DISPLAYSURF.blit(sujungBallScore, sujungBallScoreRect)


def drawHighestScore(round, score):
    highestScor = SMALLFONT.render('HIGHEST RECORD: ROUND {} SCORE {}'.format(round, score), True, WHITE)
    highestScoreRect = highestScor.get_rect()
    highestScoreRect.center = (475, 75)
    DISPLAYSURF.blit(highestScor, highestScoreRect)


def drawRound():  # 몇 라운드인지 표시
    round = BASICFONT.render('GRADE {}'.format(ROUND), True, WHITE)
    roundRect = round.get_rect()
    roundRect.center = (300, 15)
    DISPLAYSURF.blit(round, roundRect)


def terminate():
    pygame.quit()
    sys.exit()


def getBounceAmount(currentBounce, bounceRate, bounceHeight):
    # 픽셀수를 바환
    # bounceRate가 커지면 천천히 점프하는거
    # bounceHeight가 커지면 더 높이 점프하는거
    return int(math.sin((math.pi / float(bounceRate)) * currentBounce) * bounceHeight)


def getRandomVelocity():
    speed = random.randint(MINSPEED, MAXSPEED)
    if random.randint(0, 1) == 0:
        return speed
    else:
        return -speed


def getRandomOffCameraPos(camerax, cameray, objWidth, objHeight):
    # 카메라 뷰 네모를 지정하는거
    cameraRect = pygame.Rect(camerax, cameray, WINWIDTH, WINHEIGHT)
    while True:
        x = random.randint(camerax - WINWIDTH, camerax + (2 * WINWIDTH))
        y = random.randint(cameray - WINHEIGHT, cameray + (2 * WINHEIGHT))
        objRect = pygame.Rect(x, y, objWidth, objHeight)
        if not objRect.colliderect(cameraRect):
            return x, y



def makeNewGrass(camerax, cameray):
    gr = {}
    gr['grassImage'] = random.randint(0, len(GRASSIMAGES) - 1)
    gr['width'] = GRASSIMAGES[0].get_width()
    gr['height'] = GRASSIMAGES[0].get_height()
    gr['x'], gr['y'] = getRandomOffCameraPos(camerax, cameray, gr['width'], gr['height'])
    gr['rect'] = pygame.Rect((gr['x'], gr['y'], gr['width'], gr['height']))
    return gr


def isOutsideActiveArea(camerax, cameray, obj):
    #화면의 절반이 넘어가면 false를 반환
    boundsLeftEdge = camerax - WINWIDTH
    boundsTopEdge = cameray - WINHEIGHT
    boundsRect = pygame.Rect(boundsLeftEdge, boundsTopEdge, WINWIDTH * 3, WINHEIGHT * 3)
    objRect = pygame.Rect(obj['x'], obj['y'], obj['width'], obj['height'])
    return not boundsRect.colliderect(objRect)


if __name__ == '__main__':
    main()
