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
        result = self.helper(exp)[0]
        if result == float("inf"):
            await ctx.send("Invalid expression.")
            return
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        await ctx.send(result)

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
        i = 0
        while i < len(ops):
            if ops[i] == '^':
                nums[i] = self.eval(nums[i], ops[i], nums[i + 1])
                nums = nums[:i + 1] + nums[i + 2:]
                ops = ops[:i] + ops[i + 1:]
            else:
                i += 1
        i = 0
        while i < len(ops):
            if ops[i] == '*' or ops[i] == '/':
                nums[i] = self.eval(nums[i], ops[i], nums[i + 1])
                nums = nums[:i + 1] + nums[i + 2:]
                ops = ops[:i] + ops[i + 1:]
            else:
                i += 1
        i = 0
        while i < len(ops):
            if ops[i] == '+' or ops[i] == '-':
                nums[i] = self.eval(nums[i], ops[i], nums[i + 1])
                nums = nums[:i + 1] + nums[i + 2:]
                ops = ops[:i] + ops[i + 1:]
            else:
                i += 1
        return nums[0], count

    def eval(self, num1, op, num2):
        if op == '/' and num2 == 0:
            return float("inf")
        return operators[op](num1, num2)
	

def setup(client):
    client.add_cog(math(client))