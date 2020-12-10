import discord
from discord.ext import commands
from operator import truediv, mul, add, sub, pow

operators = {'+': add, '-': sub, '*': mul, 'x': mul, '×': mul, '/': truediv, '÷': truediv, '^': pow}

class math(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases = ['solve', 'calc'])
    async def calculate(self, ctx, *, expression):
        exp = ''.join(c for c in expression if c in operators or c.isdigit())
        print(exp)
        if len(exp) == 0:
            await ctx.send("Invalid expression.")
            return
        result = self.helper(exp)
        if result[1] == -1:
            await ctx.send("Error: Number limit reached.")
            return
        elif result[1] == -2:
            await ctx.send("Error: Divison by 0.")
            return
        num = result[0]
        if isinstance(num, float) and num.is_integer():
            num = int(num[0])
        await ctx.send(num)

    @calculate.error
    async def calculate_error(self, ctx, error):
        await ctx.send('Please follow format: `y.calculate {expression}`')

    def helper(self, exp):
        if len(exp) == 0:
            return 0
        nums = []
        ops = []
        num = count = 0
        while len(exp) > 0:
            c = exp[0]
            exp = exp[1:]
            if c.isdigit():
                num = num * 10 + int(c)
            else:
                if c == '(':
                    result = self.helper(exp)
                    if result[1] < 0:
                        return 0, result[1]
                    num = result[0]
                    exp = exp[result[1] + 1:]
                    count += result[1]
                elif c == ')':
                    break
                else:
                    ops.append(c)
                    nums.append(num)
                    num = 0
            count += 1
        nums.append(num)
        for n in nums:
            if n > 1000000000000:
                return 0, -1
        i = 0
        while i < len(ops):
            if ops[i] == '^':
                val = self.eval(nums[i], ops[i], nums[i + 1])
                if val == float("inf"):
                    return 0, -2
                nums[i] = val
                nums = nums[:i + 1] + nums[i + 2:]
                ops = ops[:i] + ops[i + 1:]
            else:
                i += 1
        for n in nums:
            if n > 1000000000000:
                return 0, -1
        i = 0
        while i < len(ops):
            if ops[i] in ['*', '/', '×', 'x', '÷']:
                val = self.eval(nums[i], ops[i], nums[i + 1])
                if val == float("inf"):
                    return 0, -2
                nums[i] = val
                nums = nums[:i + 1] + nums[i + 2:]
                ops = ops[:i] + ops[i + 1:]
            else:
                i += 1
        for n in nums:
            if n > 1000000000000:
                return 0, -1
        i = 0
        while i < len(ops):
            if ops[i] in ['+', '-']:
                val = self.eval(nums[i], ops[i], nums[i + 1])
                if val == float("inf"):
                    return 0, -2
                nums[i] = val
                nums = nums[:i + 1] + nums[i + 2:]
                ops = ops[:i] + ops[i + 1:]
            else:
                i += 1
        for n in nums:
            if n > 1000000000000:
                return 0, -1
        return nums[0], count

    def eval(self, num1, op, num2):
        if op == '/' and num2 == 0:
            return float("inf")
        return operators[op](num1, num2)
	
def setup(client):
    client.add_cog(math(client))